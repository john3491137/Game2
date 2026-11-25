# 小小夢港：理財夜行者

一款給國小學生的繁體中文 2.5D 理財教育遊戲。兩關分別練習預算與儲蓄、應急金與風險分散。角色、場景與道具為 Blender 原創模型；遊戲由 Godot 4.7.2 匯出為靜態網頁。

## 操作

- 鍵盤：`←` / `→` 或 `A` / `D` 移動，`Space` 跳躍，`E` 互動。
- 觸控：使用畫面上的方向、跳躍和互動按鈕。
- 走到互動物件附近開始挑戰。答錯可重試；答對後才能取得 KEY 並開啟出口。
- 關卡分數及進度只存於目前瀏覽器；「重新開始」會清除本機進度。
- 聲音預設關閉；遊戲提供音量和減少動態控制。

## Godot 執行與 Web 匯出

1. 使用 Godot 4.7.2 開啟此資料夾中的 `project.godot`。
2. 在 Godot 的匯出設定選擇 `Web`，匯出到 `docs/index.html`。CLI 指令：

   ```powershell
   C:\Godot\Godot_v4.7.2-stable_win64.exe --headless --path . --export-release Web docs/index.html
   ```

3. 把此專案推送至 GitHub。在倉庫 **Settings → Pages** 將來源設為 **Deploy from a branch**，選擇分支根目錄中的 `/docs`。
4. 等待 GitHub Pages 部署完成後，開啟顯示的網站網址。

Web 匯出依賴瀏覽器 `fetch()` 載入 `.wasm` 和 `.pck`，不能直接雙擊 `docs/index.html` 用 `file://` 開啟。若在 Pages 尚未部署前要本機預覽，請在專案根目錄執行：

```powershell
py -m http.server 8000 --directory docs
```

然後開啟 `http://localhost:8000/`。

Web 匯出使用單執行緒，GitHub Pages 不需要額外的跨來源隔離標頭。瀏覽器需支援 WebAssembly 與 WebGL 2.0。

## 教學與隱私

- 使用虛構金額和虛構投資選項，不連結真實金融商品，也不提供個人投資建議。
- 分數是遊戲內的形成性練習紀錄，不代表正式學習測驗或已驗證的學習成效。
- 遊戲不要求帳號，不會上傳玩家資料。

## 專案紀錄

- `project-brief.md`：核准的需求簡報。
- `decision-log.md`、`change-log.md`、`requirements-traceability.md`：DT–SDLC 決策、變更與需求追蹤。
- `SKILLS_USED.md`：DT–SDLC、game-design、Blender skills 的套用範圍和限制。
- `PROMPTS_TODAY.md`：今天的原始需求與後續選擇。
