# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
"""
DETR Transformer class.

Copy-paste from torch.nn.Transformer with modifications:
    * positional encodings are passed in MHattention
    * extra LN at the end of encoder is removed
    * decoder returns a stack of activations from all decoding layers
"""
import copy
from typing import Optional, List

import torch
import torch.nn.functional as F
from torch import nn, Tensor

import IPython
e = IPython.embed

class Transformer(nn.Module):

    def __init__(self, d_model=512, nhead=8, num_encoder_layers=6,
                 num_decoder_layers=6, dim_feedforward=2048, dropout=0.1,
                 activation="relu", normalize_before=False,
                 return_intermediate_dec=False):
        super().__init__()

        # 编码层
        encoder_layer = TransformerEncoderLayer(d_model, nhead, dim_feedforward,
                                                dropout, activation, normalize_before)
        # 归一化层
        encoder_norm = nn.LayerNorm(d_model) if normalize_before else None
        
        # 构建多层编码层
        self.encoder = TransformerEncoder(encoder_layer, num_encoder_layers, encoder_norm)

        # 解码层
        decoder_layer = TransformerDecoderLayer(d_model, nhead, dim_feedforward,
                                                dropout, activation, normalize_before)
        decoder_norm = nn.LayerNorm(d_model)
        
        # 构建多层解码层
        self.decoder = TransformerDecoder(decoder_layer, num_decoder_layers, decoder_norm,
                                          return_intermediate=return_intermediate_dec)

        self._reset_parameters()

        self.d_model = d_model
        self.nhead = nhead

    def _reset_parameters(self):
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)

    def forward(self, query_embed,
                src, pos, is_pad,
                robot_state_input, robot_state_pos=None,
                next_action_input=None, next_action_pos=None, next_action_is_pad=None,
                latent_input=None, latent_pos=None):
        # TODO flatten only when input has H and W
        if len(src.shape) == 4: # has H and W
            if next_action_input is not None:
                # flatten NxCxHxW to HWxNxC
                bs, c, h, w = src.shape
                src = src.flatten(2).permute(2, 0, 1)
                src_is_pad = torch.full((src.shape[1], src.shape[0]), False).to(next_action_is_pad.device)  # False: not a padding
                latent_is_pad = torch.full((latent_input.shape[1], latent_input.shape[0]), False).to(next_action_is_pad.device)  # False: not a padding
                robot_state_is_pad = torch.full((robot_state_input.shape[1], robot_state_input.shape[0]), False).to(next_action_is_pad.device)  # False: not a padding
                pos = pos.flatten(2).permute(2, 0, 1).repeat(1, bs, 1)
                query_embed = query_embed.unsqueeze(1).repeat(1, bs, 1)
                # mask = mask.flatten(1)
                robot_state_pos = robot_state_pos.unsqueeze(1).repeat(1, bs, 1)  # seq, bs, dim
                latent_pos = latent_pos.unsqueeze(1).repeat(1, bs, 1)  # seq, bs, dim
                next_action_pos = next_action_pos.unsqueeze(1).repeat(1, bs, 1)  # seq, bs, dim
                pos = torch.cat([latent_pos, pos, robot_state_pos, next_action_pos], axis=0)
                src = torch.cat([latent_input, src, robot_state_input, next_action_input], axis=0)
                is_pad = torch.cat([latent_is_pad, src_is_pad, robot_state_is_pad, next_action_is_pad], axis=1)
            else:
                # flatten NxCxHxW to HWxNxC
                bs, c, h, w = src.shape
                src = src.flatten(2).permute(2, 0, 1)
                src_is_pad = torch.full((src.shape[1], src.shape[0]), False).to(src.device)  # False: not a padding
                latent_is_pad = torch.full((latent_input.shape[1], latent_input.shape[0]), False).to(src.device)  # False: not a padding
                robot_state_is_pad = torch.full((robot_state_input.shape[1], robot_state_input.shape[0]), False).to(src.device)  # False: not a padding
                pos = pos.flatten(2).permute(2, 0, 1).repeat(1, bs, 1)
                query_embed = query_embed.unsqueeze(1).repeat(1, bs, 1)
                # mask = mask.flatten(1)
                robot_state_pos = robot_state_pos.unsqueeze(1).repeat(1, bs, 1)  # seq, bs, dim
                latent_pos = latent_pos.unsqueeze(1).repeat(1, bs, 1)  # seq, bs, dim
                pos = torch.cat([latent_pos, pos, robot_state_pos], axis=0)
                src = torch.cat([latent_input, src, robot_state_input], axis=0)
                is_pad = torch.cat([latent_is_pad, src_is_pad, robot_state_is_pad], axis=1)
        else:
            assert len(src.shape) == 3
            # flatten NxHWxC to HWxNxC
            bs, hw, c = src.shape
            src = src.permute(1, 0, 2)
            pos = pos.unsqueeze(1).repeat(1, bs, 1)
            query_embed = query_embed.unsqueeze(1).repeat(1, bs, 1)

        tgt = torch.zeros_like(query_embed)
        memory = self.encoder(src, pos=pos, src_key_padding_mask=is_pad)
        
        hs = self.decoder(tgt, memory,
                          query_pos=query_embed,
                          pos=pos,
                          memory_key_padding_mask=is_pad)

        hs = hs.transpose(1, 2)
        return hs


class TransformerEncoder(nn.Module):

    def __init__(self, encoder_layer, num_layers, norm=None):
        super().__init__()
        self.layers = _get_clones(encoder_layer, num_layers)
        self.num_layers = num_layers
        self.norm = norm

    def forward(self, src,
                pos: Optional[Tensor] = None,
                src_key_padding_mask: Optional[Tensor] = None,
                mask: Optional[Tensor] = None):
        output = src

        for layer in self.layers:
            output = layer(output,
                           pos=pos,
                           src_key_padding_mask=src_key_padding_mask,
                           src_mask=mask)

        if self.norm is not None:
            output = self.norm(output)

        return output


class TransformerDecoder(nn.Module):

    def __init__(self, decoder_layer, num_layers, norm=None, return_intermediate=False):
        super().__init__()
        self.layers = _get_clones(decoder_layer, num_layers)
        self.num_layers = num_layers
        self.norm = norm
        self.return_intermediate = return_intermediate

    def forward(self, tgt, memory,
                query_pos: Optional[Tensor] = None,
                pos: Optional[Tensor] = None,
                tgt_key_padding_mask: Optional[Tensor] = None,
                memory_key_padding_mask: Optional[Tensor] = None,
                tgt_mask: Optional[Tensor] = None,
                memory_mask: Optional[Tensor] = None):
        output = tgt

        intermediate = []

        for layer in self.layers:
            output = layer(output, memory,
                           query_pos=query_pos,
                           pos=pos,
                           tgt_key_padding_mask=tgt_key_padding_mask,
                           memory_key_padding_mask=memory_key_padding_mask,
                           tgt_mask=tgt_mask,
                           memory_mask=memory_mask)
            if self.return_intermediate:
                intermediate.append(self.norm(output))

        if self.norm is not None:
            output = self.norm(output)
            if self.return_intermediate:
                intermediate.pop()
                intermediate.append(output)

        if self.return_intermediate:
            return torch.stack(intermediate)

        return output.unsqueeze(0)


class TransformerEncoderLayer(nn.Module):

    def __init__(self, d_model, nhead, dim_feedforward=2048, dropout=0.1,
                 activation="relu", normalize_before=False):
        super().__init__()
        self.self_attn = nn.MultiheadAttention(d_model, nhead, dropout=dropout)
        # Implementation of Feedforward model
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(dim_feedforward, d_model)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

        self.activation = _get_activation_fn(activation)
        self.normalize_before = normalize_before

    def with_pos_embed(self, tensor, pos: Optional[Tensor]):
        return tensor if pos is None else tensor + pos

    def forward_post(self,
                     src,
                     pos: Optional[Tensor] = None,
                     src_key_padding_mask: Optional[Tensor] = None,
                     src_mask: Optional[Tensor] = None):
        q = k = self.with_pos_embed(src, pos)
        src2 = self.self_attn(q, k, value=src, attn_mask=src_mask,
                              key_padding_mask=src_key_padding_mask)[0]
        src = src + self.dropout1(src2)
        src = self.norm1(src)
        src2 = self.linear2(self.dropout(self.activation(self.linear1(src))))
        src = src + self.dropout2(src2)
        src = self.norm2(src)
        return src

    def forward_pre(self, src,
                    pos: Optional[Tensor] = None,
                    src_key_padding_mask: Optional[Tensor] = None,
                    src_mask: Optional[Tensor] = None):
        src2 = self.norm1(src)
        q = k = self.with_pos_embed(src2, pos)
        src2 = self.self_attn(q, k, value=src2, attn_mask=src_mask,
                              key_padding_mask=src_key_padding_mask)[0]
        src = src + self.dropout1(src2)
        src2 = self.norm2(src)
        src2 = self.linear2(self.dropout(self.activation(self.linear1(src2))))
        src = src + self.dropout2(src2)
        return src

    def forward(self, src,
                pos: Optional[Tensor] = None,
                src_key_padding_mask: Optional[Tensor] = None,
                src_mask: Optional[Tensor] = None):
        if self.normalize_before:
            return self.forward_pre(src, pos, src_key_padding_mask, src_mask)
        return self.forward_post(src, pos, src_key_padding_mask, src_mask)


class TransformerDecoderLayer(nn.Module):

    def __init__(self, d_model, nhead, dim_feedforward=2048, dropout=0.1,
                 activation="relu", normalize_before=False):
        super().__init__()
        self.self_attn = nn.MultiheadAttention(d_model, nhead, dropout=dropout)
        self.multihead_attn = nn.MultiheadAttention(d_model, nhead, dropout=dropout)
        # Implementation of Feedforward model
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(dim_feedforward, d_model)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        self.dropout3 = nn.Dropout(dropout)

        self.activation = _get_activation_fn(activation)
        self.normalize_before = normalize_before

    def with_pos_embed(self, tensor, pos: Optional[Tensor]):
        return tensor if pos is None else tensor + pos

    def forward_post(self, tgt, memory,
                     query_pos: Optional[Tensor] = None,
                     pos: Optional[Tensor] = None,
                     tgt_key_padding_mask: Optional[Tensor] = None,
                     memory_key_padding_mask: Optional[Tensor] = None,
                     tgt_mask: Optional[Tensor] = None,
                     memory_mask: Optional[Tensor] = None):
        q = k = self.with_pos_embed(tgt, query_pos)
        tgt2 = self.self_attn(q, k, value=tgt, attn_mask=tgt_mask,
                              key_padding_mask=tgt_key_padding_mask)[0]
        tgt = tgt + self.dropout1(tgt2)
        tgt = self.norm1(tgt)
        tgt2 = self.multihead_attn(query=self.with_pos_embed(tgt, query_pos),
                                   key=self.with_pos_embed(memory, pos),
                                   value=memory, attn_mask=memory_mask,
                                   key_padding_mask=memory_key_padding_mask)[0]
        tgt = tgt + self.dropout2(tgt2)
        tgt = self.norm2(tgt)
        tgt2 = self.linear2(self.dropout(self.activation(self.linear1(tgt))))
        tgt = tgt + self.dropout3(tgt2)
        tgt = self.norm3(tgt)
        return tgt

    def forward_pre(self, tgt, memory,
                    query_pos: Optional[Tensor] = None,
                    pos: Optional[Tensor] = None,
                    tgt_key_padding_mask: Optional[Tensor] = None,
                    memory_key_padding_mask: Optional[Tensor] = None,
                    tgt_mask: Optional[Tensor] = None,
                    memory_mask: Optional[Tensor] = None):
        tgt2 = self.norm1(tgt)
        q = k = self.with_pos_embed(tgt2, query_pos)
        tgt2 = self.self_attn(q, k, value=tgt2, attn_mask=tgt_mask,
                              key_padding_mask=tgt_key_padding_mask)[0]
        tgt = tgt + self.dropout1(tgt2)
        tgt2 = self.norm2(tgt)
        tgt2 = self.multihead_attn(query=self.with_pos_embed(tgt2, query_pos),
                                   key=self.with_pos_embed(memory, pos),
                                   value=memory, attn_mask=memory_mask,
                                   key_padding_mask=memory_key_padding_mask)[0]
        tgt = tgt + self.dropout2(tgt2)
        tgt2 = self.norm3(tgt)
        tgt2 = self.linear2(self.dropout(self.activation(self.linear1(tgt2))))
        tgt = tgt + self.dropout3(tgt2)
        return tgt

    def forward(self, tgt, memory,
                query_pos: Optional[Tensor] = None,
                pos: Optional[Tensor] = None,
                tgt_key_padding_mask: Optional[Tensor] = None,
                memory_key_padding_mask: Optional[Tensor] = None,
                tgt_mask: Optional[Tensor] = None,
                memory_mask: Optional[Tensor] = None):
        if self.normalize_before:
            return self.forward_pre(tgt, memory, query_pos, pos,
                                    tgt_key_padding_mask, memory_key_padding_mask, tgt_mask, memory_mask)
        return self.forward_post(tgt, memory, query_pos, pos,
                                 tgt_key_padding_mask, memory_key_padding_mask, tgt_mask, memory_mask)


def _get_clones(module, N):
    return nn.ModuleList([copy.deepcopy(module) for i in range(N)])


def build_transformer(args):
    return Transformer(
        d_model=args.hidden_dim,
        dropout=args.dropout,
        nhead=args.nheads,
        dim_feedforward=args.dim_feedforward,
        num_encoder_layers=args.enc_layers,
        num_decoder_layers=args.dec_layers,
        normalize_before=args.pre_norm,
        return_intermediate_dec=True)


def _get_activation_fn(activation):
    """Return an activation function given a string"""
    if activation == "relu":
        return F.relu
    if activation == "gelu":
        return F.gelu
    if activation == "glu":
        return F.glu
    raise RuntimeError(F"activation should be relu/gelu, not {activation}.")
