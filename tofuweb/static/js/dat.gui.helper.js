				var InitGUI = function(config, rcl2) {
					guiControls = new function() {
						this.gray_min = config["gray_min"];
						this.gray_max = config["gray_max"];
						this.steps = config["steps"];
						this.quality = config["renderer_size"][0];
						this.renderer_canvas_size = config["renderer_canvas_size"][0] + "x" + config["renderer_canvas_size"][1];
						this.absorption_mode = config["absorption_mode"];
						this.opacity_factor = config["opacity_factor"];
						this.color_factor = config["color_factor"];
						this.x_min = config["x_min"];
						this.x_max = config["x_max"];
						this.y_min = config["y_min"];
						this.y_max = config["y_max"];
						this.z_min = config["z_min"];
						this.z_max = config["z_max"];
						
						this.auto_steps = config["auto_steps"];

						this.colormap = "0";
					};

					var gui = new dat.GUI();

					var x_min_controller = gui.add(guiControls, 'x_min', 0, 1);
					x_min_controller.onChange(function(value) {
						rcl2.setGeometryMinX(value);
					});

					var x_max_controller = gui.add(guiControls, 'x_max', 0, 1);
					x_max_controller.onChange(function(value) {
						rcl2.setGeometryMaxX(value);
					});

					var y_min_controller = gui.add(guiControls, 'y_min', 0, 1);
					y_min_controller.onChange(function(value) {
						rcl2.setGeometryMinY(value);
					});

					var y_max_controller = gui.add(guiControls, 'y_max', 0, 1);
					y_max_controller.onChange(function(value) {
						rcl2.setGeometryMaxY(value);
					});

					var z_min_controller = gui.add(guiControls, 'z_min', 0, 1);
					z_min_controller.onChange(function(value) {
						rcl2.setGeometryMinZ(value);
					});

					var z_max_controller = gui.add(guiControls, 'z_max', 0, 1);
					z_max_controller.onChange(function(value) {
						rcl2.setGeometryMaxZ(value);
					});

					var steps_controller = gui.add(guiControls, 'steps', 15, 2048, 10);
					steps_controller.onFinishChange(function(value) {
						rcl2.setSteps(value);
					});

					var auto_steps_controller = gui.add(guiControls, 'auto_steps');
					auto_steps_controller.onChange(function(value) {
						rcl2.setAutoStepsOn(value);
					});

					var absorbtion_mode_controller = gui.add(guiControls, 'absorption_mode', {"MIPS": 0, "X-ray": 1, "Maximum projection intensivity": 2});
					absorbtion_mode_controller.onChange(function(value) {
						rcl2.setAbsorptionMode(value);
					});

					var color_factor_controller = gui.add(guiControls, 'color_factor', 0, 10);
					color_factor_controller.onChange(function(value) {
						rcl2.setColorFactor(value);
					});

					var opacity_factor_controller = gui.add(guiControls, 'opacity_factor', 0, 50);
					opacity_factor_controller.onChange(function(value) {
						rcl2.setOpacityFactor(value);
					});

					var gray_min_controller = gui.add(guiControls, 'gray_min', 0, 1);
					gray_min_controller.onChange(function(value) {
						rcl2.setGrayMinValue(value);
					});

					var gray_max_controller = gui.add(guiControls, 'gray_max', 0, 1);
					gray_max_controller.onChange(function(value) {
						rcl2.setGrayMaxValue(value);
					});

					var quality_controller = gui.add(guiControls, 'quality', 1, 2048);
					quality_controller.onFinishChange(function(value) {
						rcl2.setRendererSize(value, value);
					});

					var renderer_canvas_size_controller = gui.add(guiControls, 'renderer_canvas_size');
					renderer_canvas_size_controller.onFinishChange(function(value) {
						rcl2.setRendererCanvasSize(value.split('x')[0], value.split('x')[1]);
					});

					var transfer_function_controller = gui.add(guiControls, 'colormap', {
						"parula": 0, 
						"jet": 1,
						"hsv": 2,
						"hot": 3,
						"cool": 4,
						"spring": 5,
						"summer": 6,
						"autumn": 7,
						"winter": 8,
						"gray": 9,
						"bone": 10,
						"copper": 11,
						"pink": 12
					});
					transfer_function_controller.onChange(function(value) {
						switch(value) {
							case "0": {
								rcl2.setTransferFunctionByColors([
								    {"pos": 0, "color": "#352A87"},
								    {"pos": 1, "color": "#F9FB0E"}
								]);
							} break;

							case "1": {
								rcl2.setTransferFunctionByColors([
								    {"pos": 0,   "color": "#0000ff"},
								    {"pos": 1,   "color": "#ff0000"}
								]);
							} break;

							case "2": {
								rcl2.setTransferFunctionByColors([
								    {"pos": 0,    "color": "#ff0000"},
								    {"pos": 0.25, "color": "#00ff00"},
								    {"pos": 0.5,  "color": "#0000ff"},
								    {"pos": 1,    "color": "#ff0000"}
								]);
							} break;

							case "3": {
								rcl2.setTransferFunctionByColors([
								    {"pos": 0,    "color": "#000000"},
								    {"pos": 0.25, "color": "#ff0000"},
								    {"pos": 0.5,  "color": "#ffff00"},
								    {"pos": 1,    "color": "#ffffff"}
								]);
							} break;

							case "4": {
								rcl2.setTransferFunctionByColors([
								    {"pos": 0,    "color": "#00ffff"},
								    {"pos": 1,    "color": "#E405E4"}
								]);
							} break;

							case "5": {
								rcl2.setTransferFunctionByColors([
								    {"pos": 0,    "color": "#E405E4"},
								    {"pos": 1,    "color": "#FFFF00"}
								]);
							} break;

							case "6": {
								rcl2.setTransferFunctionByColors([
								    {"pos": 0,    "color": "#008066"},
								    {"pos": 1,    "color": "#FFFF66"}
								]);
							} break;

							case "7": {
								rcl2.setTransferFunctionByColors([
								    {"pos": 0,    "color": "#ff0000"},
								    {"pos": 1,    "color": "#ffff00"}
								]);
							} break;

							case "8": {
								rcl2.setTransferFunctionByColors([
								    {"pos": 0,    "color": "#0000ff"},
								    {"pos": 1,    "color": "#00ffff"}
								]);
							} break;

							case "9": {
								rcl2.setTransferFunctionByColors([
								    {"pos": 0,    "color": "#000000"},
								    {"pos": 1,    "color": "#ffffff"}
								]);
							} break;

							case "10": {
								rcl2.setTransferFunctionByColors([
								    {"pos": 0,    "color": "#000000"},
								    {"pos": 0.5,  "color": "#788798"},
								    {"pos": 1,    "color": "#ffffff"}
								]);
							} break;

							case "11": {
								rcl2.setTransferFunctionByColors([
								    {"pos": 0,    "color": "#000000"},
								    {"pos": 1,    "color": "#FFC77F"}
								]);
							} break;

							case "12": {
								rcl2.setTransferFunctionByColors([
								    {"pos": 0,    "color": "#000000"},
								    {"pos": 0.25, "color": "#A76C6C"},
								    {"pos": 0.5,  "color": "#E8E8B4"},
								    {"pos": 1,    "color": "#ffffff"}
								]);
							} break;
						}

					});

				};
