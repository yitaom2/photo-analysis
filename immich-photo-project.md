# 人生相册项目笔记

## 项目目标

把分散在 iPhone、Android、云端的几百GB照片整合成一个：
- 统一的、安全的本地照片库（Immich 自托管）
- 按时间顺序排列的人生时间轴
- 基于 GPS 地理位置的世界地图可视化（走过的地方 + 时间）
- 可以按时段生成影片/幻灯片

---

## 环境信息

- 机器：Mac (Apple Silicon M系列)
- Docker：version 27.4.0
- Docker Compose：v2.31.0-desktop.2
- Immich 运行地址：`http://localhost:2283`
- 照片总量：几百 GB（iPhone 为主，部分 Android，部分云端）

---

## 已完成步骤

### 1. 搭建 Immich

```bash
mkdir -p ~/immich && cd ~/immich

curl -L https://github.com/immich-app/immich/releases/latest/download/docker-compose.yml -o docker-compose.yml
curl -L https://github.com/immich-app/immich/releases/latest/download/example.env -o .env

docker compose up -d
```

- `.env` 关键配置：
  - `UPLOAD_LOCATION=./library`（照片存储路径）
  - `DB_DATA_LOCATION=./postgres`（数据库路径）
- Web UI 已正常访问：`http://localhost:2283`
- 管理员账号已注册

### 2. 安装 Immich CLI

```bash
npm install -g @immich/cli
```

### 3. 获取 API Key

Web UI → 右上角头像 → Account Settings → API Keys → New API Key

### 4. CLI 登录（正确方式）

```bash
# 注意：只用 API Key，不用邮箱密码
immich login http://localhost:2283 YOUR_API_KEY
```

### 5. 上传测试照片

```bash
mkdir ~/immich-test
cp ~/Pictures/some-photo.jpg ~/immich-test/
immich upload ~/immich-test
```

---

## 照片来源整合计划

| 来源 | 导出方式 | 注意事项 |
|------|----------|----------|
| iPhone | Immich App 自动同步 或 Mac Image Capture 导出 | 不要用 iCloud 网页，会丢 GPS |
| Android | 连线导出 `/sdcard/DCIM/` 或 Google Takeout | Takeout 用 `immich-go` 导入保留元数据 |
| Google Photos | `takeout.google.com` 导出 | 用 `immich-go upload gp-takeout` |
| 微信照片 | `/sdcard/Pictures/WeiXin/` 手动导出 | 无 EXIF，需从文件名提取时间 |

### 批量导入命令

```bash
# Google Takeout
immich-go upload gp-takeout \
  --server http://localhost:2283 \
  --api-key YOUR_KEY \
  /path/to/takeout

# 普通文件夹
immich-go upload from-folder \
  --server http://localhost:2283 \
  --api-key YOUR_KEY \
  /path/to/photos
```

---

## GPS 数据导出脚本

从 Immich 导出所有有 GPS 的照片元数据，用于地图可视化：

```python
import requests
import json

IMMICH_URL = "http://localhost:2283/api"
API_KEY = "你的API_KEY"
headers = {"x-api-key": API_KEY, "Accept": "application/json"}

def export_gps_data():
    assets = []
    page = 1
    while True:
        resp = requests.post(
            f"{IMMICH_URL}/assets/search",
            headers=headers,
            json={"page": page, "size": 1000, "withExif": True}
        )
        data = resp.json()
        batch = data.get("assets", {}).get("items", [])
        if not batch:
            break
        assets.extend(batch)
        page += 1

    points = []
    for a in assets:
        exif = a.get("exifInfo", {})
        lat = exif.get("latitude")
        lng = exif.get("longitude")
        if lat and lng:
            points.append({
                "lat": lat,
                "lng": lng,
                "date": a.get("fileCreatedAt", "")[:10],
                "city": exif.get("city", ""),
                "country": exif.get("country", ""),
                "id": a["id"]
            })

    with open("gps_data.json", "w") as f:
        json.dump(points, f, ensure_ascii=False, indent=2)

    print(f"导出了 {len(points)} 个有GPS的照片")
    return points

export_gps_data()
```

---

## 下一步计划

### 近期（先跑通流程）
- [ ] 上传一批真实 iPhone 照片测试
- [ ] 运行 GPS 导出脚本，确认数据格式
- [ ] 做世界地图可视化页面（按时间筛选 + 点击城市看照片）

### 中期（全量导入）
- [ ] iPhone 全量导入（Immich App 自动同步）
- [ ] Android 照片导出并导入
- [ ] Google Takeout 导入
- [ ] 处理微信照片时间问题（用文件名提取时间戳写回 EXIF）

### 长期（功能扩展）
- [ ] 按时段自动生成影片（ffmpeg + moviepy）
- [ ] 3-2-1 备份策略（本地 + 外置硬盘 + 云端冷存储）
- [ ] 扩容到外置硬盘

---

## 备份策略（待实施）

```
3 份数据
├── Immich 服务器本地（主库）
├── 外置硬盘（本地备份）
└── Backblaze B2 或 Cloudflare R2（云端冷存储）
```

数据库定时备份：
```bash
docker exec immich_postgres pg_dumpall -U postgres > backup_$(date +%Y%m%d).sql
```

---

## 技术栈总览

```
照片管理     Immich（自托管）
批量导入     immich-go、Immich CLI
元数据修复   exiftool、piexif
地图可视化   Mapbox GL JS 或 Deck.gl + React
视频生成     ffmpeg + moviepy
数据库       PostgreSQL（Immich内置）
备份         Backblaze B2 / Cloudflare R2
```
