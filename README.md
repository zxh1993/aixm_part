# aixm

`aixm` 是内部项目共用的 Python 工具包，当前主要保留：

- `aixm.utils`：路径、日志、Redis、常用工具函数。
- `aixm.zrpc`：基于 Redis 队列的内部 RPC 工具。

## 安装

支持 Python 3.8 及以上版本。

运行时外部依赖：

- `redis>=4.2.0`

## 配置

配置读取顺序为：环境变量、配置文件、默认值。
