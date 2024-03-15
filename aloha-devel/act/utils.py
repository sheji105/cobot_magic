# import numpy as np
# import torch
# import os
# import h5py
# from torch.utils.data import TensorDataset, DataLoader
# import random
# import fnmatch
# import IPython
# e = IPython.embed
#
#
# def flatten_list(target):
#     return [item for sublist in target for item in sublist]
#
#
# def find_all_hdf5(dataset_dir):
#     hdf5_files = []
#     for root, dirs, files in os.walk(dataset_dir):
#         for filename in fnmatch.filter(files, '*.hdf5'):
#             hdf5_files.append(os.path.join(root, filename))
#     print(f'Found {len(hdf5_files)} hdf5 files')
#     return hdf5_files
#
#
# def batch_sampler(batch_size, episode_len_list, sample_weights):
#     sample_probs = np.array(sample_weights) / np.sum(sample_weights) if sample_weights is not None else None
#     sum_dataset_len_l = np.cumsum([0] + [np.sum(episode_len) for episode_len in episode_len_list])
#     while True:
#         batch = []
#         for _ in range(batch_size):
#             episode_idx = np.random.choice(len(episode_len_list), p=sample_probs)
#             step_idx = np.random.randint(sum_dataset_len_l[episode_idx], sum_dataset_len_l[episode_idx + 1])
#             batch.append(step_idx)
#         yield batch
#
#
# def get_norm_stats(dataset_path_list, use_robot_base):
#     all_qpos_data = []
#     all_action_data = []
#     all_episode_len = []
#
#     for dataset_path in dataset_path_list:
#         try:
#             with h5py.File(dataset_path, 'r') as root:
#                 qpos = root['/observations/qpos'][()]
#                 qvel = root['/observations/qvel'][()]
#                 action = root['/action'][()]
#                 if use_robot_base:
#                     qpos = np.concatenate((qpos, root['/base_action'][()]), axis=1)
#                     action = np.concatenate((action, root['/base_action'][()]), axis=1)
#         except Exception as e:
#             print(f'Error loading {dataset_path} in get_norm_stats')
#             print(e)
#             quit()
#         all_qpos_data.append(torch.from_numpy(qpos))
#         all_action_data.append(torch.from_numpy(action))
#         all_episode_len.append(len(qpos))
#     all_qpos_data = torch.cat(all_qpos_data, dim=0)
#     all_action_data = torch.cat(all_action_data, dim=0)
#
#     # normalize action data
#     action_mean = all_action_data.mean(dim=[0]).float()
#     action_std = all_action_data.std(dim=[0]).float()
#     action_std = torch.clip(action_std, 1e-2, np.inf)  # clipping
#
#     # normalize qpos data
#     qpos_mean = all_qpos_data.mean(dim=[0]).float()
#     qpos_std = all_qpos_data.std(dim=[0]).float()
#     qpos_std = torch.clip(qpos_std, 1e-2, np.inf)  # clipping
#
#     action_min = all_action_data.min(dim=0).values.float()
#     action_max = all_action_data.max(dim=0).values.float()
#
#     eps = 0.0001
#     stats = {"action_mean": action_mean.numpy(), "action_std": action_std.numpy(),
#              "action_min": action_min.numpy() - eps,"action_max": action_max.numpy() + eps,
#              "qpos_mean": qpos_mean.numpy(), "qpos_std": qpos_std.numpy(),
#              "example_qpos": qpos}
#
#     return stats, all_episode_len
#
#
# class EpisodicDataset(torch.utils.data.Dataset):
#
#     def __init__(self, dataset_path_list, camera_names, norm_stats, episode_ids, episode_len, chunk_size, arm_delay_time, max_pos_lookahead,
#                  use_dataset_action, use_depth_image, use_robot_base):
#         super(EpisodicDataset).__init__()
#         self.episode_ids = episode_ids
#         self.dataset_path_list = dataset_path_list
#         self.camera_names = camera_names
#         self.norm_stats = norm_stats
#         self.episode_len = episode_len
#         self.chunk_size = chunk_size
#         self.cumulative_len = np.cumsum(self.episode_len)
#         self.max_episode_len = max(episode_len)
#         self.is_sim = None
#         self.max_pos_lookahead = max_pos_lookahead
#         self.use_dataset_action = use_dataset_action
#         self.use_depth_image = use_depth_image
#         self.arm_delay_time = arm_delay_time
#         self.use_robot_base = use_robot_base
#         self.__getitem__(0)  # initialize self.is_sim
#
#     def _locate_transition(self, index):
#         assert index < self.cumulative_len[-1]
#         episode_index = np.argmax(self.cumulative_len > index)  # argmax returns first True index
#         start_ts = index - (self.cumulative_len[episode_index] - self.episode_len[episode_index])
#         episode_id = self.episode_ids[episode_index]
#         return episode_id, start_ts
#
#     # def __len__(self):
#     #     return sum(self.episode_len)
#
#     def __getitem__(self, index):
#         episode_id, start_ts = self._locate_transition(index)
#         dataset_path = self.dataset_path_list[episode_id]
#
#         with h5py.File(dataset_path, 'r') as root:
#             is_sim = root.attrs['sim']
#             original_action_shape = root['/action'].shape
#             max_action_len = original_action_shape[0]  # max_episode
#             if self.use_robot_base:
#                 original_action_shape = (original_action_shape[0], original_action_shape[1] + 2)
#
#             start_ts = np.random.choice(max_action_len)  # 随机抽取一个索引
#             next_action_size = random.randint(0, self.max_pos_lookahead)
#             if self.use_dataset_action:
#                 actions = root['/action']
#             else:
#                 actions = root['/observations/qpos'][1:]
#                 actions = np.append(actions, actions[-1][np.newaxis, :], axis=0)
#             end_next_action_index = min(start_ts + next_action_size, max_action_len - 1)
#             qpos = root['/observations/qpos'][start_ts]
#             if self.use_robot_base:
#                 qpos = np.concatenate((qpos, root['/base_action'][start_ts]), axis=0)
#             image_dict = dict()
#             image_depth_dict = dict()
#             for cam_name in self.camera_names:
#                 image_dict[cam_name] = root[f'/observations/images/{cam_name}'][start_ts]
#                 if self.use_depth_image:
#                     image_depth_dict[cam_name] = root[f'/observations/images_depth/{cam_name}'][start_ts]
#
#             start_action = end_next_action_index
#             # action = actions[start_action:]
#             # next_action = actions[start_ts:start_action]
#             # action_len = max_action_len - start_action
#             # next_action_len = start_action - start_ts
#             index = max(0, start_action - self.arm_delay_time)
#             # print("qpos:", qpos[7:-2])
#             action = actions[index:]  # hack, to make timesteps more aligned
#             # print("action:", action[:30, 7:-2])
#             next_action = actions[start_ts:index]
#             if self.use_robot_base:
#                 action = np.concatenate((action, root['/base_action'][index:]), axis=1)
#                 next_action = np.concatenate((next_action, root['/base_action'][start_ts:index]), axis=1)
#             action_len = max_action_len - index  # hack, to make timesteps more aligned
#             next_action_len = index - start_ts
#             # if is_sim:
#             #     action = actions[start_action:]
#             #     next_action = actions[start_ts:start_action]
#             #     action_len = max_action_len - start_action
#             #     next_action_len = start_action - start_ts
#             # else:
#             #     index = max(0, start_action - 1)
#             #     action = actions[index:]  # hack, to make timesteps more aligned
#             #     next_action = actions[start_ts:index]
#             #     action_len = max_action_len - index  # hack, to make timesteps more aligned
#             #     next_action_len = index - start_ts
#
#         self.is_sim = is_sim
#
#         padded_action = np.zeros(original_action_shape, dtype=np.float32)
#         padded_action[:action_len] = action
#         action_is_pad = np.zeros(max_action_len)
#         action_is_pad[action_len:] = 1
#         padded_action = padded_action[:self.chunk_size]
#         action_is_pad = action_is_pad[:self.chunk_size]
#
#         padded_next_action = np.zeros((self.max_pos_lookahead, original_action_shape[1]), dtype=np.float32)
#         next_action_is_pad = np.zeros(self.max_pos_lookahead)
#         if next_action_len <= 0:
#             next_action_is_pad[:] = 1
#         else:
#             padded_next_action[:next_action_len] = next_action
#             next_action_is_pad[next_action_len:] = 1
#
#         all_cam_images = []
#         for cam_name in self.camera_names:
#             all_cam_images.append(image_dict[cam_name])
#         all_cam_images = np.stack(all_cam_images, axis=0)
#         # construct observations
#         image_data = torch.from_numpy(all_cam_images)
#         image_data = torch.einsum('k h w c -> k c h w', image_data)
#         image_data = image_data / 255.0
#
#         image_depth_data = np.zeros(1, dtype=np.float32)
#         if self.use_depth_image:
#             all_cam_images_depth = []
#             for cam_name in self.camera_names:
#                 all_cam_images_depth.append(image_depth_dict[cam_name])
#             all_cam_images_depth = np.stack(all_cam_images_depth, axis=0)
#             # construct observations
#             image_depth_data = torch.from_numpy(all_cam_images_depth)
#             # image_depth_data = torch.einsum('k h w c -> k c h w', image_depth_data)
#             image_depth_data = image_depth_data / 255.0
#
#         qpos_data = torch.from_numpy(qpos).float()
#         qpos_data = (qpos_data - self.norm_stats["qpos_mean"]) / self.norm_stats["qpos_std"]
#         next_action_data = torch.from_numpy(padded_next_action).float()
#         next_action_is_pad = torch.from_numpy(next_action_is_pad).bool()
#         action_data = torch.from_numpy(padded_action).float()
#         action_is_pad = torch.from_numpy(action_is_pad).bool()
#         if self.use_dataset_action:
#             next_action_data = (next_action_data - self.norm_stats["action_mean"]) / self.norm_stats["action_std"]
#             action_data = (action_data - self.norm_stats["action_mean"]) / self.norm_stats["action_std"]
#         else:
#             next_action_data = (next_action_data - self.norm_stats["qpos_mean"]) / self.norm_stats["qpos_std"]
#             action_data = (action_data - self.norm_stats["qpos_mean"]) / self.norm_stats["qpos_std"]
#
#         # torch.set_printoptions(precision=10, sci_mode=False)
#         # torch.set_printoptions(threshold=float('inf'))
#         # print("qpos_data:", qpos_data[7:])
#         # print("action_data:", action_data[:, 7:])
#
#         return image_data, image_depth_data, qpos_data, next_action_data, next_action_is_pad, action_data, action_is_pad
#
#
# def load_data(dataset_dir_list, arm_delay_time, max_pos_lookahead, use_dataset_action, use_depth_image, use_robot_base, camera_names, batch_size_train, batch_size_val, chunk_size, stats_dir_l=None, sample_weights=None, train_ratio=0.99):
#     if type(dataset_dir_list) == str:
#         dataset_dir_list = [dataset_dir_list]
#     dataset_path_list_list = [find_all_hdf5(dataset_dir) for dataset_dir in dataset_dir_list]
#     num_episodes_0 = len(dataset_path_list_list[0])
#     dataset_path_list = flatten_list(dataset_path_list_list)
#     num_episodes_list = [0] + [len(dataset_path_list) for dataset_path_list in dataset_path_list_list]
#     num_episodes_cumsum = np.cumsum(num_episodes_list)
#
#     train_episode_ids_list = []
#     val_episode_ids_list = []
#     # obtain train test split on dataset_dir_l[0]
#     for i in range(len(dataset_path_list_list)):
#         num_episodes = len(dataset_path_list_list[i])
#         shuffled_episode_ids = np.random.permutation(num_episodes)
#         train_episode_ids = shuffled_episode_ids[:int(train_ratio * num_episodes)]
#         val_episode_ids = shuffled_episode_ids[int(train_ratio * num_episodes):]
#         train_episode_ids_list.append(np.array([train_id+num_episodes_cumsum[i] for train_id in train_episode_ids]))
#         val_episode_ids_list.append(np.array([val_id+num_episodes_cumsum[i] for val_id in val_episode_ids]))
#     train_episode_ids = np.concatenate(train_episode_ids_list)
#     val_episode_ids = np.concatenate(val_episode_ids_list)
#
#     # obtain train test split on dataset_dir_l[0]
#     # shuffled_episode_ids_0 = np.random.permutation(num_episodes_0)
#     # train_episode_ids_0 = shuffled_episode_ids_0[:int(train_ratio * num_episodes_0)]
#     # val_episode_ids_0 = shuffled_episode_ids_0[int(train_ratio * num_episodes_0):]
#     # train_episode_ids_list = [train_episode_ids_0] + [np.arange(num_episodes) + num_episodes_cumsum[idx] for idx, num_episodes in enumerate(num_episodes_list[1:])]
#     # val_episode_ids_list = [val_episode_ids_0]
#     # train_episode_ids = np.concatenate(train_episode_ids_list)
#     # val_episode_ids = np.concatenate(val_episode_ids_list)
#     print(f'\n\nData from: {dataset_dir_list}\n- Train on {[len(x) for x in train_episode_ids_list]} episodes\n- Test on {[len(x) for x in val_episode_ids_list]} episodes\n\n')
#
#     _, all_episode_len = get_norm_stats(dataset_path_list, use_robot_base)
#     train_episode_len_list = [[all_episode_len[i] for i in train_episode_ids] for train_episode_ids in train_episode_ids_list]
#     val_episode_len_list = [[all_episode_len[i] for i in val_episode_ids] for val_episode_ids in val_episode_ids_list]
#     train_episode_len = flatten_list(train_episode_len_list)
#     val_episode_len = flatten_list(val_episode_len_list)
#     if stats_dir_l is None:
#         stats_dir_l = dataset_dir_list
#     elif type(stats_dir_l) == str:
#         stats_dir_l = [stats_dir_l]
#     norm_stats, _ = get_norm_stats(flatten_list([find_all_hdf5(stats_dir) for stats_dir in stats_dir_l]), use_robot_base)
#     print(f'Norm stats from: {stats_dir_l}')
#
#     batch_sampler_train = batch_sampler(batch_size_train, train_episode_len_list, sample_weights)
#     batch_sampler_val = batch_sampler(batch_size_val, val_episode_len_list, None)
#
#     # construct dataset and dataloader
#     train_dataset = EpisodicDataset(dataset_path_list, camera_names, norm_stats, train_episode_ids, train_episode_len, chunk_size,
#                                     arm_delay_time, max_pos_lookahead, use_dataset_action, use_depth_image, use_robot_base)
#     val_dataset = EpisodicDataset(dataset_path_list, camera_names, norm_stats, val_episode_ids, val_episode_len, chunk_size,
#                                   arm_delay_time, max_pos_lookahead, use_dataset_action, use_depth_image, use_robot_base)
#     train_num_workers = 1
#     val_num_workers = 1
#     train_dataloader = DataLoader(train_dataset, batch_sampler=batch_sampler_train, pin_memory=True, num_workers=train_num_workers, prefetch_factor=1)
#     val_dataloader = DataLoader(val_dataset, batch_sampler=batch_sampler_val, pin_memory=True, num_workers=val_num_workers, prefetch_factor=1)
#
#     return train_dataloader, val_dataloader, norm_stats, train_dataset.is_sim
#
#
# # env utils
# def sample_box_pose():
#     x_range = [0.0, 0.2]
#     y_range = [0.4, 0.6]
#     z_range = [0.05, 0.05]
#
#     ranges = np.vstack([x_range, y_range, z_range])
#
#     cube_position = np.random.uniform(ranges[:, 0], ranges[:, 1])
#
#     cube_quat = np.array([1, 0, 0, 0])
#     return np.concatenate([cube_position, cube_quat])
#
#
# def sample_insertion_pose():
#     # Peg
#     x_range = [0.1, 0.2]
#     y_range = [0.4, 0.6]
#     z_range = [0.05, 0.05]
#
#     ranges = np.vstack([x_range, y_range, z_range])
#     peg_position = np.random.uniform(ranges[:, 0], ranges[:, 1])
#
#     peg_quat = np.array([1, 0, 0, 0])
#     peg_pose = np.concatenate([peg_position, peg_quat])
#
#     # Socket
#     x_range = [-0.2, -0.1]
#     y_range = [0.4, 0.6]
#     z_range = [0.05, 0.05]
#
#     ranges = np.vstack([x_range, y_range, z_range])
#     socket_position = np.random.uniform(ranges[:, 0], ranges[:, 1])
#
#     socket_quat = np.array([1, 0, 0, 0])
#     socket_pose = np.concatenate([socket_position, socket_quat])
#
#     return peg_pose, socket_pose
#
#
# # helper functions
# def compute_dict_mean(epoch_dicts):
#     result = {k: None for k in epoch_dicts[0]}
#     num_items = len(epoch_dicts)
#     for k in result:
#         value_sum = 0
#         for epoch_dict in epoch_dicts:
#             value_sum += epoch_dict[k]
#         result[k] = value_sum / num_items
#     return result
#
#
# def detach_dict(d):
#     new_d = dict()
#     for k, v in d.items():
#         new_d[k] = v.detach()
#     return new_d
#
#
# def set_seed(seed):
#     torch.manual_seed(seed)
#     np.random.seed(seed)


import numpy as np
import torch
import os
import h5py
from torch.utils.data import TensorDataset, DataLoader
import random
import IPython

e = IPython.embed
import cv2

class EpisodicDataset(torch.utils.data.Dataset):

    def __init__(self, episode_ids, dataset_dir, camera_names, norm_stats, arm_delay_time, max_pos_lookahead,
                 use_dataset_action, use_depth_image, use_robot_base):
        super(EpisodicDataset).__init__()
        self.episode_ids = episode_ids  # 1000
        self.dataset_dir = dataset_dir
        self.camera_names = camera_names
        self.norm_stats = norm_stats
        self.is_sim = None
        self.max_pos_lookahead = max_pos_lookahead
        self.use_dataset_action = use_dataset_action
        self.use_depth_image = use_depth_image
        self.arm_delay_time = arm_delay_time
        self.use_robot_base = use_robot_base
        self.__getitem__(0)  # initialize self.is_sim

    def __len__(self):
        return len(self.episode_ids)

    def __getitem__(self, index):
        episode_id = self.episode_ids[index]
        # 读取数据
        dataset_path = os.path.join(self.dataset_dir, f'episode_{episode_id}.hdf5')

        with h5py.File(dataset_path, 'r') as root:
            is_sim = root.attrs['sim']
            is_compress = root.attrs['compress']
            original_action_shape = root['/action'].shape
            max_action_len = original_action_shape[0]  # max_episode
            if self.use_robot_base:
                original_action_shape = (original_action_shape[0], original_action_shape[1] + 2)

            start_ts = np.random.choice(max_action_len)  # 随机抽取一个索引
            next_action_size = random.randint(0, self.max_pos_lookahead)
            if self.use_dataset_action:
                actions = root['/action']
            else:
                actions = root['/observations/qpos'][1:]
                actions = np.append(actions, actions[-1][np.newaxis, :], axis=0)
            end_next_action_index = min(start_ts + next_action_size, max_action_len - 1)
            qpos = root['/observations/qpos'][start_ts]
            if self.use_robot_base:
                qpos = np.concatenate((qpos, root['/base_action'][start_ts]), axis=0)
            image_dict = dict()
            image_depth_dict = dict()
            for cam_name in self.camera_names:
                if is_compress:
                    decoded_image = root[f'/observations/images/{cam_name}'][start_ts]
                    image_dict[cam_name] = cv2.imdecode(decoded_image, 1)
                    # print(image_dict[cam_name].shape)
                    # exit(-1)
                else:
                    image_dict[cam_name] = root[f'/observations/images/{cam_name}'][start_ts]

                if self.use_depth_image:
                    image_depth_dict[cam_name] = root[f'/observations/images_depth/{cam_name}'][start_ts]

            start_action = end_next_action_index
            # action = actions[start_action:]
            # next_action = actions[start_ts:start_action]
            # action_len = max_action_len - start_action
            # next_action_len = start_action - start_ts
            index = max(0, start_action - self.arm_delay_time)
            # print("qpos:", qpos[7:-2])
            action = actions[index:]  # hack, to make timesteps more aligned
            # print("action:", action[:30, 7:-2])
            next_action = actions[start_ts:index]
            if self.use_robot_base:
                action = np.concatenate((action, root['/base_action'][index:]), axis=1)
                next_action = np.concatenate((next_action, root['/base_action'][start_ts:index]), axis=1)
            action_len = max_action_len - index  # hack, to make timesteps more aligned
            next_action_len = index - start_ts
            # if is_sim:
            #     action = actions[start_action:]
            #     next_action = actions[start_ts:start_action]
            #     action_len = max_action_len - start_action
            #     next_action_len = start_action - start_ts
            # else:
            #     index = max(0, start_action - 1)
            #     action = actions[index:]  # hack, to make timesteps more aligned
            #     next_action = actions[start_ts:index]
            #     action_len = max_action_len - index  # hack, to make timesteps more aligned
            #     next_action_len = index - start_ts

        self.is_sim = is_sim

        padded_action = np.zeros(original_action_shape, dtype=np.float32)
        padded_action[:action_len] = action
        action_is_pad = np.zeros(max_action_len)
        action_is_pad[action_len:] = 1
        padded_next_action = np.zeros((self.max_pos_lookahead, original_action_shape[1]), dtype=np.float32)

        next_action_is_pad = np.zeros(self.max_pos_lookahead)
        if next_action_len <= 0:
            next_action_is_pad[:] = 1
        else:
            padded_next_action[:next_action_len] = next_action
            next_action_is_pad[next_action_len:] = 1

        all_cam_images = []
        for cam_name in self.camera_names:
            all_cam_images.append(image_dict[cam_name])
        all_cam_images = np.stack(all_cam_images, axis=0)
        # construct observations
        image_data = torch.from_numpy(all_cam_images)
        image_data = torch.einsum('k h w c -> k c h w', image_data)
        image_data = image_data / 255.0

        image_depth_data = np.zeros(1, dtype=np.float32)
        if self.use_depth_image:
            all_cam_images_depth = []
            for cam_name in self.camera_names:
                all_cam_images_depth.append(image_depth_dict[cam_name])
            all_cam_images_depth = np.stack(all_cam_images_depth, axis=0)
            # construct observations
            image_depth_data = torch.from_numpy(all_cam_images_depth)
            # image_depth_data = torch.einsum('k h w c -> k c h w', image_depth_data)
            image_depth_data = image_depth_data / 255.0

        qpos_data = torch.from_numpy(qpos).float()
        qpos_data = (qpos_data - self.norm_stats["qpos_mean"]) / self.norm_stats["qpos_std"]
        next_action_data = torch.from_numpy(padded_next_action).float()
        next_action_is_pad = torch.from_numpy(next_action_is_pad).bool()
        action_data = torch.from_numpy(padded_action).float()
        action_is_pad = torch.from_numpy(action_is_pad).bool()
        if self.use_dataset_action:
            next_action_data = (next_action_data - self.norm_stats["action_mean"]) / self.norm_stats["action_std"]
            action_data = (action_data - self.norm_stats["action_mean"]) / self.norm_stats["action_std"]
        else:
            next_action_data = (next_action_data - self.norm_stats["qpos_mean"]) / self.norm_stats["qpos_std"]
            action_data = (action_data - self.norm_stats["qpos_mean"]) / self.norm_stats["qpos_std"]

        # torch.set_printoptions(precision=10, sci_mode=False)
        # torch.set_printoptions(threshold=float('inf'))
        # print("qpos_data:", qpos_data[7:])
        # print("action_data:", action_data[:, 7:])

        return image_data, image_depth_data, qpos_data, next_action_data, next_action_is_pad, action_data, action_is_pad


def get_norm_stats(dataset_dir, num_episodes, use_robot_base):
    all_qpos_data = []
    all_action_data = []

    for episode_idx in range(num_episodes):
        dataset_path = os.path.join(dataset_dir, f'episode_{episode_idx}.hdf5')
        with h5py.File(dataset_path, 'r') as root:
            qpos = root['/observations/qpos'][()]
            qvel = root['/observations/qvel'][()]
            action = root['/action'][()]
            if use_robot_base:
                qpos = np.concatenate((qpos, root['/base_action'][()]), axis=1)
                action = np.concatenate((action, root['/base_action'][()]), axis=1)
        all_qpos_data.append(torch.from_numpy(qpos))
        all_action_data.append(torch.from_numpy(action))

    all_qpos_data = torch.stack(all_qpos_data)
    all_action_data = torch.stack(all_action_data)
    all_action_data = all_action_data

    # normalize action data
    action_mean = all_action_data.mean(dim=[0, 1], keepdim=True)
    action_std = all_action_data.std(dim=[0, 1], keepdim=True)
    action_std = torch.clip(action_std, 1e-2, np.inf)  # clipping

    # normalize qpos data
    qpos_mean = all_qpos_data.mean(dim=[0, 1], keepdim=True)
    qpos_std = all_qpos_data.std(dim=[0, 1], keepdim=True)
    qpos_std = torch.clip(qpos_std, 1e-2, np.inf)  # clipping

    stats = {"action_mean": action_mean.numpy().squeeze(), "action_std": action_std.numpy().squeeze(),
             "qpos_mean": qpos_mean.numpy().squeeze(), "qpos_std": qpos_std.numpy().squeeze(),
             "example_qpos": qpos}

    return stats


def load_data(dataset_dir, num_episodes, arm_delay_time, max_pos_lookahead, use_dataset_action, use_depth_image,
              use_robot_base, camera_names, batch_size_train, batch_size_val):
    print(f'\nData from: {dataset_dir}\n')
    # obtain train test split
    train_ratio = 0.8  # 数据集比例
    shuffled_indices = np.random.permutation(num_episodes)  # 打乱

    train_indices = shuffled_indices[:int(train_ratio * num_episodes)]
    val_indices = shuffled_indices[int(train_ratio * num_episodes):]

    # obtain normalization stats for qpos and action  返回均值和方差
    norm_stats = get_norm_stats(dataset_dir, num_episodes, use_robot_base)

    # construct dataset and dataloader 归一化处理  结构化处理数据
    train_dataset = EpisodicDataset(train_indices, dataset_dir, camera_names, norm_stats, arm_delay_time,
                                    max_pos_lookahead,
                                    use_dataset_action, use_depth_image, use_robot_base)

    val_dataset = EpisodicDataset(val_indices, dataset_dir, camera_names, norm_stats, arm_delay_time, max_pos_lookahead,
                                  use_dataset_action, use_depth_image, use_robot_base)

    train_dataloader = DataLoader(train_dataset, batch_size=batch_size_train, shuffle=True, pin_memory=True,
                                  num_workers=1, prefetch_factor=1)

    val_dataloader = DataLoader(val_dataset, batch_size=batch_size_val, shuffle=True, pin_memory=True, num_workers=1,
                                prefetch_factor=1)

    return train_dataloader, val_dataloader, norm_stats, train_dataset.is_sim


# env utils
def sample_box_pose():
    x_range = [0.0, 0.2]
    y_range = [0.4, 0.6]
    z_range = [0.05, 0.05]

    ranges = np.vstack([x_range, y_range, z_range])

    cube_position = np.random.uniform(ranges[:, 0], ranges[:, 1])

    cube_quat = np.array([1, 0, 0, 0])
    return np.concatenate([cube_position, cube_quat])


def sample_insertion_pose():
    # Peg
    x_range = [0.1, 0.2]
    y_range = [0.4, 0.6]
    z_range = [0.05, 0.05]

    ranges = np.vstack([x_range, y_range, z_range])
    peg_position = np.random.uniform(ranges[:, 0], ranges[:, 1])

    peg_quat = np.array([1, 0, 0, 0])
    peg_pose = np.concatenate([peg_position, peg_quat])

    # Socket
    x_range = [-0.2, -0.1]
    y_range = [0.4, 0.6]
    z_range = [0.05, 0.05]

    ranges = np.vstack([x_range, y_range, z_range])
    socket_position = np.random.uniform(ranges[:, 0], ranges[:, 1])

    socket_quat = np.array([1, 0, 0, 0])
    socket_pose = np.concatenate([socket_position, socket_quat])

    return peg_pose, socket_pose


# helper functions
def compute_dict_mean(epoch_dicts):
    result = {k: None for k in epoch_dicts[0]}
    num_items = len(epoch_dicts)
    for k in result:
        value_sum = 0
        for epoch_dict in epoch_dicts:
            value_sum += epoch_dict[k]
        result[k] = value_sum / num_items
    return result


def detach_dict(d):
    new_d = dict()
    for k, v in d.items():
        new_d[k] = v.detach()
    return new_d


def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
