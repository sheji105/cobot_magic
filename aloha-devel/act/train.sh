num_epochs=600
batch_size=48
echo $(pwd)

ws_path=$(pwd)
cd $ws_path

train_dir=$HOME/train0315

python act/train.py --dataset /media/lin/T7/data0314/ --ckpt_dir $train_dir/pretrain --batch_size $batch_size --pretrain_ckpt_dir ~/train0312/policy_best.ckpt --num_epochs $num_epochs
python act/train.py --dataset /media/lin/T7/data0314/ --ckpt_dir $train_dir/no_pretrain --batch_size $batch_size --num_epochs $num_epochs