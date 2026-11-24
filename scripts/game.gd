extends Node3D

const HERO_PATH := "res://assets/models/dreamer.glb"
const LEVEL_PATHS := {
	1: "res://assets/models/fog_ledger_hall.glb",
	2: "res://assets/models/risk_channel.glb",
}
const SAVE_PATH := "user://dream_harbor_progress.cfg"
const FLOOR_TOP := 0.27
const GRAVITY := 22.0
const WALK_SPEED := 3.4

var current_stage := 1
var scores := [0, 0]
var solved := [false, false]
var keys_collected := [false, false]
var finished := false
var attempts := 0
var reduce_motion := false
var audio_enabled := false
var left_held := false
var right_held := false
var jump_queued := false

var stage_root: Node3D
var player: CharacterBody3D
var key_model: Node3D
var gate_door: Node3D
var camera: Camera3D
var quiz_layer: Control
var quiz_question: Label
var quiz_feedback: Label
var choice_box: VBoxContainer
var ending_layer: Control
var ending_body: Label
var hint_label: Label
var score_label: Label
var stage_label: Label
var key_label: Label
var challenge_label: Label
var controls_panel: PanelContainer
var audio_player: AudioStreamPlayer
var ambient_player: AudioStreamPlayer
var volume_slider: HSlider
var font_file: FontFile


func _ready() -> void:
	_load_progress()
	font_file = load("res://assets/fonts/NotoSansTC-VF.ttf") as FontFile
	_build_world()
	_build_interface()
	_refresh_hud()
	if finished:
		_show_ending()
	else:
		_set_hint(_default_hint())


func _input(event: InputEvent) -> void:
	if event is InputEventKey:
		var pressed: bool = event.pressed and not event.echo
		if event.keycode in [KEY_LEFT, KEY_A]:
			left_held = event.pressed
		if event.keycode in [KEY_RIGHT, KEY_D]:
			right_held = event.pressed
		if pressed and event.keycode in [KEY_E, KEY_ENTER]:
			_interact()
		if pressed and event.keycode in [KEY_SPACE, KEY_UP, KEY_W]:
			jump_queued = true


func _physics_process(delta: float) -> void:
	if player == null or quiz_layer.visible or ending_layer.visible:
		return
	var axis := float(right_held) - float(left_held)
	player.velocity.x = axis * WALK_SPEED
	player.velocity.z = 0.0
	if not player.is_on_floor():
		player.velocity.y -= GRAVITY * delta
	elif jump_queued:
		player.velocity.y = 7.1
	jump_queued = false
	player.move_and_slide()
	player.position.x = clampf(player.position.x, -7.4, 7.15)
	if absf(axis) > 0.01:
		var hero_model := player.get_node_or_null("DreamerModel") as Node3D
		if hero_model:
			hero_model.rotation.y = 0.0 if axis > 0.0 else PI


func _build_world() -> void:
	var env := WorldEnvironment.new()
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color("#17131c") if current_stage == 1 else Color("#121c28")
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color("#97889b") if current_stage == 1 else Color("#7f9fb0")
	environment.ambient_light_energy = 0.55
	env.environment = environment
	add_child(env)

	var key_light := DirectionalLight3D.new()
	key_light.rotation_degrees = Vector3(-35, -18, 0)
	key_light.light_color = Color("#e9c38b")
	key_light.light_energy = 1.25
	add_child(key_light)
	var fill_light := OmniLight3D.new()
	fill_light.position = Vector3(-2.7, 2.6, 1.8)
	fill_light.light_color = Color("#d98743")
	fill_light.light_energy = 2.0
	fill_light.omni_range = 7.0
	add_child(fill_light)

	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 9.6
	camera.position = Vector3(0.0, 5.0, 17.0)
	camera.look_at(Vector3(0.0, 2.25, 0.0), Vector3.UP)
	camera.current = true
	add_child(camera)

	stage_root = Node3D.new()
	stage_root.name = "StageEnvironment"
	add_child(stage_root)
	var packed := load(LEVEL_PATHS[current_stage]) as PackedScene
	if packed:
		stage_root.add_child(packed.instantiate())

	var floor_body := StaticBody3D.new()
	floor_body.name = "FloorCollision"
	var floor_shape := CollisionShape3D.new()
	var box_shape := BoxShape3D.new()
	box_shape.size = Vector3(18.0, 0.28, 6.0)
	floor_shape.shape = box_shape
	floor_shape.position = Vector3(0.0, FLOOR_TOP - 0.14, 0.0)
	floor_body.add_child(floor_shape)
	add_child(floor_body)

	key_model = stage_root.find_child("KEY", true, false) as Node3D
	gate_door = stage_root.find_child("GateDoor", true, false) as Node3D
	if key_model:
		key_model.visible = solved[current_stage - 1] and not keys_collected[current_stage - 1]
	if gate_door and solved[current_stage - 1]:
		_open_gate(true)

	player = CharacterBody3D.new()
	player.name = "Player"
	player.position = Vector3(-6.4, FLOOR_TOP, 0.0)
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.32
	capsule.height = 1.65
	var player_collider := CollisionShape3D.new()
	player_collider.shape = capsule
	player_collider.position.y = 0.80
	player.add_child(player_collider)
	var hero_pack := load(HERO_PATH) as PackedScene
	if hero_pack:
		var hero := hero_pack.instantiate() as Node3D
		hero.name = "DreamerModel"
		hero.scale = Vector3.ONE * 0.95
		player.add_child(hero)
	add_child(player)


func _build_interface() -> void:
	var layer := CanvasLayer.new()
	layer.name = "GameInterface"
	add_child(layer)
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.theme = _make_theme()
	layer.add_child(root)

	var header := _make_panel(root, Vector4(0.02, 0.02, 0.98, 0.12), Color("#211d27"), Color("#9e794d"))
	var header_row := HBoxContainer.new()
	header_row.add_theme_constant_override("separation", 18)
	header.add_child(header_row)
	var title := _label("夢港夜行者", 27, Color("#f0c275"))
	title.custom_minimum_size.x = 260
	header_row.add_child(title)
	stage_label = _label("第 1 關｜霧市帳本", 22)
	stage_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header_row.add_child(stage_label)
	key_label = _label("KEY 0/1", 19, Color("#d7c5a5"))
	header_row.add_child(key_label)
	score_label = _label("本關 0 分", 22, Color("#f0c275"))
	score_label.custom_minimum_size.x = 155
	header_row.add_child(score_label)

	var challenge := _make_panel(root, Vector4(0.52, 0.14, 0.98, 0.34), Color("#29242e"), Color("#755940"))
	challenge_label = _label("", 20, Color("#eee4d8"))
	challenge_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	challenge.add_child(challenge_label)

	controls_panel = _make_panel(root, Vector4(0.02, 0.84, 0.45, 0.98), Color("#211d27"), Color("#755940"))
	var controls := HBoxContainer.new()
	controls.add_theme_constant_override("separation", 8)
	controls_panel.add_child(controls)
	var left_button := _button("←", 18)
	left_button.pressed.connect(_step_player.bind(-0.7))
	controls.add_child(left_button)
	var right_button := _button("→", 18)
	right_button.pressed.connect(_step_player.bind(0.7))
	controls.add_child(right_button)
	var jump_button := _button("跳躍", 17)
	jump_button.pressed.connect(func(): jump_queued = true)
	controls.add_child(jump_button)
	var interact_button := _button("互動", 17)
	interact_button.pressed.connect(_interact)
	controls.add_child(interact_button)

	var hint_panel := _make_panel(root, Vector4(0.47, 0.84, 0.98, 0.98), Color("#211d27"), Color("#755940"))
	var hint_col := VBoxContainer.new()
	hint_col.add_theme_constant_override("separation", 2)
	hint_panel.add_child(hint_col)
	hint_label = _label("← → 移動｜Space 跳躍｜E 互動", 17, Color("#e7ddcf"))
	hint_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	hint_col.add_child(hint_label)
	var toggles := HBoxContainer.new()
	hint_col.add_child(toggles)
	var audio_toggle := _button("聲音：關", 14)
	audio_toggle.pressed.connect(_toggle_audio.bind(audio_toggle))
	toggles.add_child(audio_toggle)
	var motion_toggle := _button("減少動態：關", 14)
	motion_toggle.pressed.connect(_toggle_motion.bind(motion_toggle))
	toggles.add_child(motion_toggle)
	volume_slider = HSlider.new()
	volume_slider.min_value = 0.0
	volume_slider.max_value = 1.0
	volume_slider.step = 0.05
	volume_slider.value = 0.45
	volume_slider.custom_minimum_size = Vector2(110, 18)
	volume_slider.value_changed.connect(_set_volume)
	toggles.add_child(volume_slider)
	_set_volume(volume_slider.value)

	quiz_layer = Control.new()
	quiz_layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	quiz_layer.visible = false
	root.add_child(quiz_layer)
	var dim := ColorRect.new()
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.color = Color(0.035, 0.025, 0.045, 0.78)
	quiz_layer.add_child(dim)
	var quiz_panel := _make_panel(quiz_layer, Vector4(0.15, 0.20, 0.85, 0.82), Color("#211b24"), Color("#bf9252"))
	var quiz_col := VBoxContainer.new()
	quiz_col.add_theme_constant_override("separation", 12)
	quiz_panel.add_child(quiz_col)
	quiz_question = _label("", 25, Color("#fff3df"))
	quiz_question.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	quiz_col.add_child(quiz_question)
	quiz_feedback = _label("選一個做法，看看夢港會發生什麼事。", 18, Color("#e9c98f"))
	quiz_feedback.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	quiz_col.add_child(quiz_feedback)
	choice_box = VBoxContainer.new()
	choice_box.add_theme_constant_override("separation", 8)
	quiz_col.add_child(choice_box)
	var close_button := _button("先離開", 17)
	close_button.pressed.connect(_close_quiz)
	quiz_col.add_child(close_button)

	ending_layer = Control.new()
	ending_layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	ending_layer.visible = false
	root.add_child(ending_layer)
	var ending_dim := ColorRect.new()
	ending_dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	ending_dim.color = Color(0.035, 0.025, 0.045, 0.88)
	ending_layer.add_child(ending_dim)
	var ending_panel := _make_panel(ending_layer, Vector4(0.17, 0.19, 0.83, 0.83), Color("#211b24"), Color("#bf9252"))
	var ending_col := VBoxContainer.new()
	ending_col.add_theme_constant_override("separation", 14)
	ending_panel.add_child(ending_col)
	ending_col.add_child(_label("夢港的理財成長紀錄", 30, Color("#f0c275")))
	ending_body = _label("", 21, Color("#f4eadc"))
	ending_body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	ending_col.add_child(ending_body)
	var ending_note := _label("遊戲分數是練習紀錄，不等同正式學習測驗。", 16, Color("#c9b9a3"))
	ending_note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	ending_col.add_child(ending_note)
	var restart_button := _button("重新開始", 19)
	restart_button.pressed.connect(_restart_game)
	ending_col.add_child(restart_button)

	audio_player = AudioStreamPlayer.new()
	add_child(audio_player)
	ambient_player = AudioStreamPlayer.new()
	ambient_player.volume_db = -24.0
	add_child(ambient_player)
	ambient_player.stream = _make_tone(82.0, 88.0, 1.6, 0.035, true)
	_set_controls_visible(not finished)


func _make_theme() -> Theme:
	var theme := Theme.new()
	if font_file:
		theme.default_font = font_file
	theme.default_font_size = 20
	theme.set_color("font_color", "Button", Color("#f4eadc"))
	theme.set_color("font_hover_color", "Button", Color("#fff8eb"))
	var normal := StyleBoxFlat.new()
	normal.bg_color = Color("#49404a")
	normal.border_color = Color("#a17b50")
	normal.set_border_width_all(1)
	normal.set_corner_radius_all(7)
	normal.content_margin_left = 12
	normal.content_margin_right = 12
	normal.content_margin_top = 8
	normal.content_margin_bottom = 8
	theme.set_stylebox("normal", "Button", normal)
	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = Color("#5a4b50")
	theme.set_stylebox("hover", "Button", hover)
	var pressed := normal.duplicate() as StyleBoxFlat
	pressed.bg_color = Color("#80613e")
	theme.set_stylebox("pressed", "Button", pressed)
	return theme


func _make_panel(parent: Control, anchors: Vector4, color: Color, border: Color) -> PanelContainer:
	var panel := PanelContainer.new()
	panel.anchor_left = anchors.x
	panel.anchor_top = anchors.y
	panel.anchor_right = anchors.z
	panel.anchor_bottom = anchors.w
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.border_color = border
	style.set_border_width_all(2)
	style.set_corner_radius_all(9)
	style.content_margin_left = 16
	style.content_margin_right = 16
	style.content_margin_top = 10
	style.content_margin_bottom = 10
	panel.add_theme_stylebox_override("panel", style)
	parent.add_child(panel)
	return panel


func _label(value: String, font_size: int, color: Color = Color("#f4eadc")) -> Label:
	var label := Label.new()
	label.text = value
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	return label


func _button(value: String, font_size: int) -> Button:
	var button := Button.new()
	button.text = value
	button.add_theme_font_size_override("font_size", font_size)
	button.custom_minimum_size = Vector2(0, 44)
	button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return button


func _refresh_hud() -> void:
	if stage_label == null:
		return
	stage_label.text = "第 1 關｜霧市帳本" if current_stage == 1 else "第 2 關｜風險航道"
	score_label.text = "本關 %d 分" % scores[current_stage - 1]
	key_label.text = "KEY %d/1" % int(keys_collected[current_stage - 1])
	if current_stage == 1:
		challenge_label.text = "小挑戰：50 元先支付 30 元必要花費\n目標：安排儲蓄，再考慮想要的物品。"
	else:
		challenge_label.text = "小挑戰：40 枚夢晶要怎麼安排？\n目標：保留應急金，並認識分散風險。"


func _default_hint() -> String:
	if finished:
		return "兩把 KEY 都已找到，夢港的門已打開。"
	if solved[current_stage - 1]:
		return "挑戰完成！找到金色 KEY，再走到門邊按 E。"
	return "← → 或 A/D 移動｜Space 跳躍｜走近帳本後按 E 互動。"


func _set_hint(message: String) -> void:
	if hint_label:
		hint_label.text = message


func _set_controls_visible(value: bool) -> void:
	if controls_panel:
		controls_panel.visible = value and not quiz_layer.visible and not ending_layer.visible


func _step_player(amount: float) -> void:
	if player and not quiz_layer.visible and not ending_layer.visible:
		player.position.x = clampf(player.position.x + amount, -7.4, 7.15)


func _interact() -> void:
	if quiz_layer == null or quiz_layer.visible or ending_layer.visible or player == null:
		return
	var x := player.position.x
	if not solved[current_stage - 1]:
		var altar_x := -1.0 if current_stage == 1 else -0.4
		if absf(x - altar_x) <= 2.2:
			_show_quiz()
		else:
			_set_hint("往中央的帳本／天秤走近，再按 E 開始互動。")
		return
	if not keys_collected[current_stage - 1]:
		if x >= 4.3:
			keys_collected[current_stage - 1] = true
			_save_progress()
			_refresh_hud()
			_play_effect("key")
			_set_hint("拿到 KEY！走向出口，再按 E。")
		else:
			_set_hint("金色 KEY 已出現，走近它並按 E 拿取。")
		return
	if x >= 5.35:
		if current_stage == 1:
			current_stage = 2
			_save_progress()
			get_tree().reload_current_scene()
		else:
			finished = true
			_save_progress()
			_show_ending()
	else:
		_set_hint("出口在右側，走到門邊按 E。")


func _show_quiz() -> void:
	attempts = 0
	quiz_question.text = _question_for_stage()
	quiz_feedback.text = "選一個做法，看看夢港會發生什麼事。"
	for child in choice_box.get_children():
		child.queue_free()
	var options := _options_for_stage()
	for i in range(options.size()):
		var option_button := _button(options[i], 18)
		option_button.pressed.connect(_answer.bind(i))
		choice_box.add_child(option_button)
	quiz_layer.visible = true
	_set_controls_visible(false)


func _question_for_stage() -> String:
	if current_stage == 1:
		return "霧市帳本｜你有 50 元，先付 30 元的交通與餐點。\n剩下 20 元，哪個安排能先存下 10 元？"
	return "風險航道｜你有 40 枚夢晶。哪個計畫比較能照顧突發需要並分散風險？"


func _options_for_stage() -> Array[String]:
	if current_stage == 1:
		return [
			"A｜把 20 元全拿去買貼紙，今天不存錢。",
			"B｜先存 10 元，剩下 10 元再買想要的物品。",
			"C｜存 5 元，剩下 15 元買想要的物品。",
		]
	return [
		"A｜全部放進一個說保證翻倍的神秘盒子。",
		"B｜先留 10 枚應急金，再把 30 枚分到兩個不同夢島。",
		"C｜不留應急金，把 40 枚都放到同一座夢島。",
	]


func _answer(index: int) -> void:
	attempts += 1
	if index != 1:
		quiz_feedback.text = "再想想：先照顧必要需要，也要留一點餘裕。可以再試一次。" if current_stage == 1 else "再想想：保證高報酬要小心；保留應急金並分散選擇。再試一次。"
		_play_effect("wrong")
		return
	solved[current_stage - 1] = true
	scores[current_stage - 1] = maxi(50, 100 - (attempts - 1) * 20)
	quiz_layer.visible = false
	_set_controls_visible(true)
	if key_model:
		key_model.visible = true
	_open_gate(false)
	_save_progress()
	_refresh_hud()
	_set_hint("答對！你完成本關目標，KEY 出現並為本關加分。走近 KEY 按 E 拿取。")
	_play_effect("success")


func _close_quiz() -> void:
	quiz_layer.visible = false
	_set_controls_visible(true)
	_set_hint("靠近互動物件後可再按 E 開啟挑戰。")


func _open_gate(immediate: bool) -> void:
	if gate_door == null:
		return
	var destination := gate_door.position.x + 1.15
	if immediate or reduce_motion:
		gate_door.position.x = destination
	else:
		var tween := create_tween()
		tween.tween_property(gate_door, "position:x", destination, 0.7)


func _show_ending() -> void:
	if ending_layer == null:
		return
	ending_body.text = "第一關｜預算規劃：%d / 100 分\n第二關｜風險判斷：%d / 100 分\n\n你已完成 2 / 2 個理財技能節點。\n成長路徑：先安排需要、儲蓄與想要，再為突發狀況留餘裕並分散風險。\n\n總分：%d / 200" % [scores[0], scores[1], scores[0] + scores[1]]
	ending_layer.visible = true
	_set_controls_visible(false)
	_play_effect("success")


func _restart_game() -> void:
	scores = [0, 0]
	solved = [false, false]
	keys_collected = [false, false]
	current_stage = 1
	finished = false
	attempts = 0
	_save_progress()
	get_tree().reload_current_scene()


func _toggle_audio(button: Button) -> void:
	audio_enabled = not audio_enabled
	AudioServer.set_bus_mute(0, not audio_enabled)
	button.text = "聲音：開" if audio_enabled else "聲音：關"
	if audio_enabled:
		ambient_player.play()
	else:
		ambient_player.stop()


func _toggle_motion(button: Button) -> void:
	reduce_motion = not reduce_motion
	button.text = "減少動態：開" if reduce_motion else "減少動態：關"
	_save_progress()


func _set_volume(value: float) -> void:
	AudioServer.set_bus_volume_linear(0, value)


func _play_effect(kind: String) -> void:
	if not audio_enabled or audio_player == null:
		return
	if kind == "wrong":
		audio_player.stream = _make_tone(260.0, 185.0, 0.22, 0.12, false)
	elif kind == "key":
		audio_player.stream = _make_tone(620.0, 760.0, 0.20, 0.13, false)
	else:
		audio_player.stream = _make_tone(440.0, 820.0, 0.34, 0.13, false)
	audio_player.play()


func _make_tone(start_hz: float, end_hz: float, duration: float, amplitude: float, looping: bool) -> AudioStreamWAV:
	var rate := 22050
	var frames := int(rate * duration)
	var data := PackedByteArray()
	data.resize(frames * 2)
	for i in range(frames):
		var t := float(i) / float(rate)
		var ratio := float(i) / float(maxi(1, frames - 1))
		var hz := lerpf(start_hz, end_hz, ratio)
		var envelope := 1.0 if looping else (1.0 - ratio) * minf(1.0, ratio * 12.0)
		var sample := sin(TAU * hz * t) * amplitude * envelope
		data.encode_s16(i * 2, int(sample * 32767.0))
	var stream := AudioStreamWAV.new()
	stream.format = AudioStreamWAV.FORMAT_16_BITS
	stream.mix_rate = rate
	stream.stereo = false
	stream.data = data
	if looping:
		stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
		stream.loop_begin = 0
		stream.loop_end = frames
	return stream


func _load_progress() -> void:
	var config := ConfigFile.new()
	if config.load(SAVE_PATH) != OK:
		return
	scores = config.get_value("game", "scores", [0, 0])
	solved = config.get_value("game", "solved", [false, false])
	keys_collected = config.get_value("game", "keys", [false, false])
	current_stage = clampi(int(config.get_value("game", "stage", 1)), 1, 2)
	finished = bool(config.get_value("game", "finished", false))
	reduce_motion = bool(config.get_value("accessibility", "reduce_motion", false))


func _save_progress() -> void:
	var config := ConfigFile.new()
	config.set_value("game", "scores", scores)
	config.set_value("game", "solved", solved)
	config.set_value("game", "keys", keys_collected)
	config.set_value("game", "stage", current_stage)
	config.set_value("game", "finished", finished)
	config.set_value("accessibility", "reduce_motion", reduce_motion)
	config.save(SAVE_PATH)

