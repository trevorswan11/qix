package window

import rl "vendor:raylib"

launch :: proc() {
	rl.InitWindow(200, 200, "Qix")
	defer rl.CloseWindow()

	for (!rl.WindowShouldClose()) {
		rl.PollInputEvents()
	}
}
