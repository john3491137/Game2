# 需求追蹤

| ID | 需求 | 實作位置 | 驗證證據 |
|---|---|---|---|
| R-01 | 繁體中文，適合國小閱讀 | `scripts/game.gd`, `assets/fonts/` | Web 啟動畫面及關卡畫面 |
| R-02 | 2.5D 陰暗探索氛圍與原創 3D 模型 | `assets/models/`, `assets/blender/` | GLB 匯入與場景截圖 |
| R-03 | 第一關預算互動；答對才能取得 KEY | `scripts/game.gd` | 遊戲操作流程 |
| R-04 | 第二關投資風險互動；答對才能取得 KEY | `scripts/game.gd` | 遊戲操作流程 |
| R-05 | 每關顯示分數 | `scripts/game.gd` | HUD 和結算摘要 |
| R-06 | 最後顯示進步／技能成果 | `scripts/game.gd` | 兩關完成摘要 |
| R-07 | 可由 Godot 匯出並部署 GitHub Pages | `export_presets.cfg`, `docs/` | Web 匯出檔與 README 步驟 |
| R-08 | 鍵盤及觸控可用，減少動態效果可切換 | `scripts/game.gd` | Browser smoke verification |
| R-09 | 不蒐集或上傳個資，進度本機儲存 | `scripts/game.gd` | `user://` 儲存流程 |
