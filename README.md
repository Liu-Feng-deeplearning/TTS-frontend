# TTS-frontend

tts的前端，包括文本归一化，多音字预测，韵律预测等。

### 预测

##### 使用示例
python3 tts_frondend_main.py hparams.yaml input_path output_path

可以在hparams.yaml中更改相关配置
- 只预测拼音: nnet_phone=False, flag_psd=False
- 使用神经网络预测拼音: nnet_phone=True
- 预测拼音和韵律: nnet_phone=False, flag_psd=True

### 数据准备
原始csv文件（TTS标准数据的文本格式）-> pkl格式文件。 Note: 只保留含有多音字的条目

具体脚本:
python3 -m src.train.extract_feature
python3 -m src.train.extract_psd_feature

---

### 训练

##### 示例
CUDA_VISIBLE_DEVICES=gpu_num python3  -m  src.train.train  models/v3/           
CUDA_VISIBLE_DEVICES=gpu_num python3  -m  src.train.prosody_train  models/psd_v1/       
 
##### 训练数据：
- phone：～154k items(eval ~5k)
- posody：21k items(eval ~500)

##### 模型：BERT+CRF-blstm
- BERT模型来源于google开源模型
- 分类模型：kashgari （https://kashgari.bmio.net/）

---
### 评测 

##### 拼音准确率评测（5k items）
- 字典+规则：0.075/0.135 （字错误率/多音字错误率）
- nnet model+后处理: 0.062/0.049

##### 韵律准确率评测
- 分词规则: 0.43 (标签错误率)
- nnet model: 0.175 

### todo
1. bert-embedding和后续的模型拆分开，不重复计算。
2. ~~hdf转pb，补充必备的单元测试脚本~~
3. 性能评估和优化
4. ~~C++代码实现 模型推理~~
5. ~~C++代码实现 后处理和正则化~~

---
### Details

#### 几个常用文件
- pronunciation_diationary: 发音词典      
- pronunciation_diationary_ph1: 英文字母发音词典      
- qingyin_word: 轻音词典，每个词以轻声结尾      
- simple_poly_dict: 多音字词典，记录常见多音字      

#### 使用的发音变调规则
- 协同发音 or 语流音变: 33 -> 23 333 -> 223       
- 不的特殊规则: 四声之前变二声，一二三声之前变四声。      
- 一的特殊规则: 四声之前变二声，一二三声之前变四声。      