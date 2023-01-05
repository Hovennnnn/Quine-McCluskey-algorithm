# Quine-McCluskey
奎因-麦克拉斯基算法（pku2022数电）

CSDN网址：https://blog.csdn.net/TonyChen1234/article/details/123847941

## 步骤
1. 列出所有group并按1的个数进行分组；
2. 进行多次合并，找到所有主蕴含项；
3. 找到质主蕴含项；
4. 用最少的PI覆盖剩余的minterm（这里用BFS的方法）。
