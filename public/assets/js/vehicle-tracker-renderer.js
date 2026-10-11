/* Delivered public vanilla renderer; native wrapper/path adapter. Source SHA256: ca2c6879275ff8085d457f37aa5b050a4f9e101f7a7338c7facb2c7f866ee899 */
(function () {
	gsap.defaults({ overwrite: 'auto' });
	gsap.config({ nullTargetWarn: false });

	var urlParams = new URLSearchParams(window.location.search);
	var webcast = urlParams.has('webcast') && urlParams.get('webcast') === 'true';

	var deviceSettings = {
		isWebGL: false,
		isAndroid: null,
		isIEMobile: null,
		isiPod: null,
		isiPhone: null,
		isiPad: null,
		isiOS: null,
		isMobile: null,
		isTablet: null,
		isWinSafari: null,
		isMacSafari: null
		};

	var vehicleTrackerElement = document.querySelector("vehicle-tracker");
var serviceUrls = JSON.parse(vehicleTrackerElement.querySelector(".tracker-path-map").textContent);
var assetUrls = serviceUrls.assets;
var frozenServices = document.querySelector('meta[name="spacex-service-mode"]')?.content === "frozen" || new URLSearchParams(location.search).get("referenceServices") === "frozen";

	function setupDeviceSettings() {
		var ua = navigator.userAgent.toLowerCase();
		deviceSettings.isAndroid = ua.indexOf("android") > -1;
		deviceSettings.isiPod = navigator.userAgent.match(/iPod/i) !== null;
		deviceSettings.isiPhone = navigator.userAgent.match(/iPhone/i) !== null;
		deviceSettings.isiPad = navigator.userAgent.match(/iPad/i) !== null;
		deviceSettings.isiOS = (navigator.userAgent.match(/(iPad|iPhone|iPod)/i) ? true : false);
		deviceSettings.isIEMobile = navigator.userAgent.match(/iemobile/i) !== null;

		var p = navigator.platform.toLowerCase();

		var vehicleTrackerBody = vehicleTrackerElement.querySelector("[data-tracker-root]");

		if (deviceSettings.isIEMobile || deviceSettings.isAndroid || deviceSettings.isiPhone || deviceSettings.isiPad || p === 'ipad' || p === 'iphone' || p === 'ipod' || p === 'android' || p === 'palm' || p === 'windows phone' || p === 'blackberry' || p === 'linux armv7l') {
			deviceSettings.isMobile = true;
			vehicleTrackerBody.className += 'isMobile';
		} else {
			vehicleTrackerBody.className += 'isDesktop';
		}

		if (webcast) {
			vehicleTrackerBody.className += ' webcast';
		}
	}

	var i,
		x, y,
		camera,
		scene,
		renderer,
		container,
		$ = vehicleTrackerElement.querySelector.bind(vehicleTrackerElement),
		width  = window.innerWidth,
		height = window.innerHeight,
		windowHalfX = width / 2,
		windowHalfY = height / 2,
		isWebglAliasing = true,
		toRAD = Math.PI/180,
		mouse = new THREE.Vector2(), mouseX = 0, mouseY = 0,
		mouseXOnMouseDown = 0, mouseYOnMouseDown = 0,
		clientMouseX = 0, clientMouseY = 0, initMouseX,
		openingCameraZ = 30000,
		baseCameraZ = 30000,
		baseCameraX = 3250,
		targetCameraZ = baseCameraZ,
		targetRotationX = 0,
		targetRotationY = 0,
		targetRotationZ = 0,
		targetRotationXOnMouseDown = 0,
		targetRotationYOnMouseDown = 0,
		lastTouchX, lastTouchY,
		dragSpeed = 0.1,
		iconSize = 28,
		distanceToMeters = 1000,
		isMouseDown = false, isMouseMoved = false,
		isRotated = false, isEventsEnabled = false;

	var currentVehicles = {};
	var vehicleTrajectoryColor = new THREE.Color("#FFFFFF"); //00D1FF

	function initWebgl() {
		setupDeviceSettings();

		container = $('#interactive');
		scene = new THREE.Scene();
		camera = new THREE.PerspectiveCamera( 35, width / height, 0.5, baseCameraZ * 2 );
		camera.position.x = 0;
		camera.position.y = 0;
		camera.position.z = openingCameraZ;
		camera.rotation.x = 0;
		camera.rotation.y = 0;
		camera.rotation.z = 0;
		camera.rotation.order = 'YXZ';
		scene.add( camera );

		if (deviceSettings.isMobile) {
			isWebglAliasing = false;
		}

		renderer = new THREE.WebGLRenderer({ alpha: false, antialias: isWebglAliasing });
		var devicePixelRatio = window.devicePixelRatio = window.devicePixelRatio || window.screen.deviceXDPI / window.screen.logicalXDPI;
		renderer.setPixelRatio(devicePixelRatio);
		renderer.setSize(width, height);
		renderer.setClearColor (0x000000, 1);
		container.appendChild( renderer.domElement );
		renderer.compile(scene, camera);

		window.addEventListener( 'resize', onWindowResize, false );
		onWindowResize();

		animate();

		initPreloader();
	}

	var loadingManager = new THREE.LoadingManager(),
		textureLoader = new THREE.TextureLoader(loadingManager),
		texturesLoaded,
		texturesTotal;

	function initPreloader() {
		issTexture = textureLoader.load(assetUrls["assets/images/vehicle-tracker/icon_iss.png"]);
		dragonTexture = textureLoader.load(assetUrls["assets/images/vehicle-tracker/icon_dragon.png"]);
		dragonIssTexture = textureLoader.load(assetUrls["assets/images/vehicle-tracker/icon_dragon_iss.png"]);
		dragonIssTexture2 = textureLoader.load(assetUrls["assets/images/vehicle-tracker/icon_dragon_iss2.png"]);
		starshipTexture = textureLoader.load(assetUrls["assets/images/vehicle-tracker/icon_starship.png"]);
		starshipTexture2 = textureLoader.load(assetUrls["assets/images/vehicle-tracker/icon_starship2.png"]);

		if (deviceSettings.isMobile) {
			earthTexture = textureLoader.load(assetUrls["assets/images/vehicle-tracker/earth/earth_dragon_ui_mobile.jpg"]);
			earthGlowTexture = textureLoader.load(assetUrls["assets/images/vehicle-tracker/glow_mobile.jpg"]);
		} else {
			earthTexture = textureLoader.load(assetUrls["assets/images/vehicle-tracker/earth/earth_dragon_ui.jpg"]);
			earthGlowTexture = textureLoader.load(assetUrls["assets/images/vehicle-tracker/glow.jpg"]);
		}

		loadingManager.onProgress = function ( url, itemsLoaded, itemsTotal ) {
			renderer.compile(scene, camera);
			texturesTotal = itemsTotal;
			texturesLoaded = itemsLoaded;
			var tempPercentage = Math.round( itemsLoaded / itemsTotal * 100 );
			updatePreloader(tempPercentage);
		};

		loadingManager.onLoad = function () {
			initExperience();
		};

		createScene();
		createEarth();
		createISS();
		createVehicles();
		startPreloader();
	}

	function startPreloader() {
		gsap.set( "#preloader-circle .circle-color, #preloader-circle .circle-grey", { drawSVG: "0% 0%", autoAlpha: 0 });
		gsap.set( "#preloader-circle", { rotation: -90 });
		var preloaderAnimationIn =  new TimelineMax({ paused: true } );
		preloaderAnimationIn.fromTo( "#preloader-circle .circle-grey", 3, { drawSVG: "0% 0%" }, { drawSVG: "0% 102%", ease: "expo.inOut" }, 0);
		preloaderAnimationIn.to( "#preloader-circle .circle-color", 1, { autoAlpha: 1 }, 1);
		preloaderAnimationIn.fromTo( "#preloader-inner, #preloader-circle .circle-grey", 1, { autoAlpha: 0 }, { autoAlpha: 1, ease: "none"}, 0 );
		preloaderAnimationIn.play(0);
	}

	function updatePreloader(percent) {
		var preloaderPercent = percent;
		gsap.to( "#preloader-circle .circle-color", 1, { drawSVG: "0% " + preloaderPercent + "%", immediateRender: false, ease: "expo.out" });
		$('#preloader-percent').innerHTML = preloaderPercent;
	}

	function hidePreloader() {
		var preloaderAnimationOut =  new TimelineMax({ paused: true });
		preloaderAnimationOut.to( "#preloader", 1, { autoAlpha: 0, ease: "none" }, 1);
		preloaderAnimationOut.play(0);
		isEventsEnabled = true;
		//isRotated = true;
	}

	// INIT EXPERIENCE
	function initExperience() {
		var interactiveContainer = $('#interactive');
		if (deviceSettings.isMobile) {
			interactiveContainer.addEventListener( 'touchstart', onDocumentTouchStart, false );
			interactiveContainer.addEventListener( 'touchmove', onDocumentTouchMove, false );
			interactiveContainer.addEventListener( 'touchend', onDocumentTouchEnd, false );
		} else  {
			interactiveContainer.addEventListener( 'mousedown', onDocumentMouseDown, false );
			interactiveContainer.addEventListener( 'mousemove', onDocumentMouseMove, false );
			interactiveContainer.addEventListener( 'mouseup', onDocumentMouseUp, false );
			//interactiveContainer.addEventListener( 'mousewheel', onMouseWheel, false);
			interactiveContainer.addEventListener( 'mouseleave', onDocumentMouseLeave, false );
		}
		renderer.compile(scene, camera);
		hidePreloader();
		onWindowResize();
	}

	// SCENE ////////////////////////////////////////
	var rotationObject,
		vehiclesObject;

	function createScene() {
		rotationObject  = new THREE.Group();
		rotationObject.position.x = baseCameraX;
		scene.add(rotationObject);

		earthObject = new THREE.Group();
		rotationObject.add(earthObject);

		issObject = new THREE.Group();
		issObject.rotation.x = -90 * toRAD;
		rotationObject.add(issObject);

		vehiclesObject = new THREE.Group();
		vehiclesObject.rotation.x = -90 * toRAD;
		rotationObject.add(vehiclesObject);
	}

	// EARTH ////////////////////////////////////////
	var earthObject,
		earthRadius = 6378.14,
		earthSafeZone = earthRadius + 500,
		earthCenter = new THREE.Vector3(0,0,0),
		earthBufferGeometry,
		earthMaterial,
		earthTexture,
		earthMesh,
		earthGlowBufferGeometry,
		earthGlowMaterial,
		earthGlowTexture,
		earthGlowMesh,
		earthGlowSize = 30000,
		earthCreated = false;

	function createEarth() {
		// EARTH GLOW
		earthGlowBufferGeometry = new THREE.PlaneBufferGeometry(earthGlowSize, earthGlowSize, 1, 1);
		earthGlowMaterial = new THREE.MeshBasicMaterial({
			map: earthGlowTexture,
			transparent: true,
			opacity: 0.5,
			blending: THREE.AdditiveBlending,
			depthWrite: false
		});
		earthGlowMesh = new THREE.Mesh( earthGlowBufferGeometry, earthGlowMaterial );
		earthGlowMesh.position.z = -5000;
		scene.add(earthGlowMesh);

		// EARTH
		earthBufferGeometry = new THREE.SphereBufferGeometry(earthRadius, 32, 32);
		earthMaterial = new THREE.MeshBasicMaterial({
			map: earthTexture
		});
		earthMesh = new THREE.Mesh(earthBufferGeometry, earthMaterial);
		renderer.compile(scene, camera);
		earthObject.add(earthMesh);

		earthCreated = true;
	}

	// ISS ////////////////////////////////////////
	var issMesh,
		issMaterial,
		issTexture,
		issTargetPosition,
		issX = 0,
		issY = 0,
		issZ = 0,
		issCreated = false;

	function createISS() {
		issTexture.anisotropy = 16;

		issGeometry = new THREE.PlaneGeometry( iconSize, iconSize, 32 );
		issMaterial = new THREE.MeshBasicMaterial( {
			map: issTexture,
			transparent: true,
			opacity: 1,
			side: THREE.DoubleSide,
			depthWrite: false
		});
		issMaterial.needsUpdate = true;
		issMesh = new THREE.Mesh( issGeometry, issMaterial );
		issMesh.visible = false;

		var tempIconSize = iconSize;
		if (deviceSettings.isMobile) {
			tempIconSize = iconSize * 2 ;
		}
		issMesh.scale.set( tempIconSize, tempIconSize, tempIconSize );
		issMesh.position.set( 0, 0, 0 );
		issObject.add(issMesh);

		issCreated = true;
	}

	function renderISS() {
		if (issCreated) {
			issMesh.lookAt( camera.position );
		}
	}

	// DRAGON ////////////////////////////////////////
	var dragonMesh,
		dragonMaterial,
		dragonTexture,
		dragonIssTexture,
		dragonIssTexture2,
		dragonCreated = false;

	function createVehicles() {
		dragonTexture.anisotropy = 16;

		dragonGeometry = new THREE.PlaneGeometry( iconSize, iconSize, 32 );
		dragonMaterial = new THREE.MeshBasicMaterial( {
			map: dragonTexture,
			transparent: true,
			opacity: 0,
			side: THREE.DoubleSide,
			depthWrite: false
		});
		dragonMaterial.needsUpdate = true;
		dragonMesh = new THREE.Mesh( dragonGeometry, dragonMaterial );
		dragonMesh.visible = false;

		var tempIconSize = iconSize;
		if (deviceSettings.isMobile) {
			tempIconSize = iconSize * 2 ;
		}
		dragonMesh.scale.set( tempIconSize, tempIconSize, tempIconSize );
		dragonMesh.position.set( 0, 0, 0 );
		vehiclesObject.add(dragonMesh);

		dragonCreated = true;

		// START THE TRACKERS
		dragonTracker = setInterval(dragonTrackerLoop, 5000);
		dragonTrackerLoop();

		starshipTracker = setInterval(starshipTrackerLoop, 5000);
		starshipTrackerLoop();
	}

	// DRAGON TELEMETRY ////////////////////////////////////////
	var	vehicleTelemetryTime = 0,
		vehicleTelemetryAltitude = 0,
		vehicleTelemetrySpeed = 0,
		vehicleTelemetryCreated = false;

	function showVehicleTelemetry() {
		vehicleTelemetryCreated = true;
		//$('#telemetry').style.display = "table";
		$('#telemetry').style.opacity = 1;
	}

	function renderVehicleTelemetry() {
		if (vehicleTelemetryCreated) {
			$('#vehicle_time').innerHTML = "T+ " + vehicleTelemetryTime;
			$('#vehicle_speed').innerHTML = vehicleTelemetrySpeed + " KM/H";
			$('#vehicle_altitude').innerHTML = vehicleTelemetryAltitude + " KM";
		}
	}

	function renderDragonVehicles() {
		for (var id in dragonVehicles) {
			var mesh = dragonVehicles[id];
			if (mesh) {
				mesh.lookAt( camera.position );
			}
		}
	}

	function renderStarshipVehicles() {
		for (var id in starshipVehicles) {
			var mesh = starshipVehicles[id];
			if (mesh) {
				mesh.lookAt( camera.position );
			}
		}
	}

	var starshipTexture,
		starshipTexture2;

	// OBJECT TRACKER ////////////////////////////////////////
	var dragonTracker;
	var starshipTracker;
	var dragonVehicles = {};
	var starshipVehicles = {};
	var dragonTrajectoryObjects = {};
	var starshipTrajectoryObjects = {};
	var dragonTrajectoryVertices = {};
	var starshipTrajectoryVertices = {};
	var allMeshes = {};
	var dragonData = {};
	var starshipData = {};
	var featuredVehicle = null;

	window.vehicles = allMeshes;

	// Dragon is present in JSON before GNC publishes a real position.
	// [0, 0, 0] means "not ready yet" — do not show a button or track it.
	function hasValidDragonPosition(vData) {
		if (!vData) {
			return false;
		}
		var pos = vData["glass.predict_dgn_r_ecef_v3"];
		if (!pos || pos.length < 3) {
			return false;
		}
		return !(pos[0] === 0 && pos[1] === 0 && pos[2] === 0);
	}

	// When prop_dgn goes stale, leading points lag behind the live vehicle.
	// Find the closest published point, drop everything behind it, and reattach
	// the line at the current position so only the forward path remains.
	function trimDragonTrajectoryToVehicle(verticesArray, vehiclePosition) {
		if (!verticesArray || verticesArray.length < 2 || !vehiclePosition) {
			return verticesArray;
		}

		var closestIdx = 0;
		var closestDist = vehiclePosition.distanceTo(verticesArray[0]);
		for (var ti = 1; ti < verticesArray.length; ti++) {
			var d = vehiclePosition.distanceTo(verticesArray[ti]);
			if (d < closestDist) {
				closestDist = d;
				closestIdx = ti;
			}
		}

		// Closest point is still the start — no lagging tail to trim
		if (closestIdx === 0) {
			return verticesArray;
		}

		// Vehicle is at/past the end of the published trajectory
		if (closestIdx >= verticesArray.length - 1) {
			return [];
		}

		// Keep the forward path from the closest point onward;
		// snap the first vertex to the live vehicle so the line starts cleanly.
		var trimmed = verticesArray.slice(closestIdx);
		trimmed[0] = vehiclePosition.clone();
		return trimmed;
	}

	function setCurrentVehicles() {
		var filteredData = {};
		Object.keys(starshipData).forEach(function(key) {
		  if (key !== "metadata") {
		    filteredData[key] = starshipData[key];
		  }
		});
		Object.keys(dragonData).forEach(function(key) {
		  if (key !== "metadata" && hasValidDragonPosition(dragonData[key])) {
		    filteredData[key] = dragonData[key];
		  }
		});
		window.currentVehicles = filteredData;
		var allIds = Object.keys(window.currentVehicles);
		// Drop featured selection if that vehicle is no longer publishable
		if (featuredVehicle != null && allIds.indexOf(featuredVehicle) === -1) {
			featuredVehicle = null;
			window.featuredVehicle = null;
		}
		if (featuredVehicle == null) {
			var starshipIds = allIds.filter(id => id.startsWith('ship'));
			var preferredId = starshipIds.length > 0 ? starshipIds[0] : (allIds.length > 0 ? allIds[0] : null);
			featuredVehicle = preferredId;
			window.featuredVehicle = preferredId;
			setFeatured(preferredId);
		}
		if (allIds.length > 0 && !vehicleTelemetryCreated) {
			showVehicleTelemetry();
		}
	}

	function dragonTrackerLoop() {
		var request = new XMLHttpRequest();
		request.open('GET', (frozenServices ? serviceUrls.snapshots["dragon_tracker_public.json"] : serviceUrls.live["dragon_tracker_public.json"]) + "?" + new Date().getTime(), true);
		//request.open('GET', './assets/json/vehicle-tracker/dragon_sample.json?'+ new Date().getTime(), true);
		request.onload = function() {
			if (this.status >= 200 && this.status < 400) {
				var data = JSON.parse(this.response);
				if (data) {
					dragonData = data;
					setCurrentVehicles();
					var vehicles = data;
					// Skip dragons that exist in JSON but have no real position yet
					var vehicleIds = Object.keys(vehicles).filter(function(id) {
						return id !== "metadata" && hasValidDragonPosition(vehicles[id]);
					});

					// REMOVE OLD VEHICLES IF NOT IN CURRENT
					// (includes dragons that lost a valid predict_dgn_r_ecef_v3)
					for (var id in dragonVehicles) {
						if (vehicleIds.indexOf(id) === -1) {
							vehiclesObject.remove(dragonVehicles[id]);
							if (dragonTrajectoryObjects[id]) {
								vehiclesObject.remove(dragonTrajectoryObjects[id]);
							}
							delete dragonVehicles[id];
							delete dragonTrajectoryObjects[id];
							delete dragonTrajectoryVertices[id];
							delete allMeshes[id];
						}
					}

					// update shared ISS from first vehicle that has ISS data
					// (may still be present even when dragon position is not yet valid)
					var issSourceId = null;
					var allDragonIds = Object.keys(vehicles).filter(function(id) { return id !== "metadata"; });
					for (var i = 0; i < allDragonIds.length; i++) {
						if (vehicles[allDragonIds[i]] && vehicles[allDragonIds[i]]["glass.predict_iss_r_ecef_v3"]) {
							issSourceId = allDragonIds[i];
							break;
						}
					}
					var hasIss = false;
					if (issSourceId && vehicles[issSourceId]["glass.predict_iss_r_ecef_v3"]) {
						issX = vehicles[issSourceId]["glass.predict_iss_r_ecef_v3"][0] / distanceToMeters;
						issY = vehicles[issSourceId]["glass.predict_iss_r_ecef_v3"][1] / distanceToMeters;
						issZ = vehicles[issSourceId]["glass.predict_iss_r_ecef_v3"][2] / distanceToMeters;
						var issVertex = new THREE.Vector3(issX, issY, issZ);
						var distance = checkDistance(issVertex, earthCenter);
						if (distance < earthSafeZone) {
							var newPosition = updateDistance(issVertex, distance);
							issX = newPosition.x;
							issY = newPosition.y;
							issZ = newPosition.z;
						}
						issMesh.position.set( issX, issY, issZ );
						hasIss = true;
						if (Math.floor(issX) == 0 && Math.floor(issY) == 0 && Math.floor(issZ) == 0) {
							hideISS();
						} else {
							showISS();
						}
					} else {
						hideISS();
					}

					// PROCESS VEHICLES
					for (var k = 0; k < vehicleIds.length; k++) {
						var id = vehicleIds[k];
						var vData = vehicles[id];
						// create if not exist
						if (!dragonVehicles[id]) {
							var vehicleMaterial = new THREE.MeshBasicMaterial( {
								map: dragonTexture,
								transparent: true,
								opacity: 0,
								side: THREE.DoubleSide,
								depthWrite: false
							});
							vehicleMaterial.needsUpdate = true;
							var vehicleGeometry = new THREE.PlaneGeometry( iconSize, iconSize, 32 );
							var vehicleMesh = new THREE.Mesh( vehicleGeometry, vehicleMaterial );
							vehicleMesh.visible = false;
							var tempIconSize = iconSize;
							if (deviceSettings.isMobile) {
								tempIconSize = iconSize * 2;
							}
							vehicleMesh.scale.set( tempIconSize, tempIconSize, tempIconSize );
							vehicleMesh.position.set( 0, 0, 0 );
							vehiclesObject.add(vehicleMesh);
							dragonVehicles[id] = vehicleMesh;
							allMeshes[id] = vehicleMesh;
						}
						var vehicleMesh = dragonVehicles[id];
						var vehicleMaterial = vehicleMesh.material;

						// UPDATE POSITIONS
						if (vData["glass.predict_dgn_r_ecef_v3"]) {
							var px = vData["glass.predict_dgn_r_ecef_v3"][0] / distanceToMeters;
							var py = vData["glass.predict_dgn_r_ecef_v3"][1] / distanceToMeters;
							var pz = vData["glass.predict_dgn_r_ecef_v3"][2] / distanceToMeters;
							var pVertex = new THREE.Vector3(px, py, pz);
							var pDistance = checkDistance(pVertex, earthCenter);
							if (pDistance < earthSafeZone) {
								var newPosition = updateDistance(pVertex, pDistance);
								px = newPosition.x;
								py = newPosition.y;
								pz = newPosition.z;
							}
							vehicleMesh.position.set( px, py, pz );
							if (vehicleMesh.visible === false) {
								vehicleMesh.visible = true;
								gsap.fromTo( vehicleMaterial, 1, { opacity: 0 }, { opacity: 1 });
							}
							if (id === featuredVehicle && !isRotated) {
								rotateToLocation(px, py, pz);
							}
						} else {
							vehicleMesh.visible = false;
						}

						// UPDATE TRAJECTORIES
						if (vData["glass.prop_dgn_r_ecef_v3"]) {
							var jsonArray = vData["glass.prop_dgn_r_ecef_v3"];
							var verticesArray = [];
							for (var j = 0; j < jsonArray.length; j++) {
								var vertex = new THREE.Vector3(
									jsonArray[j][0] / distanceToMeters,
									jsonArray[j][1] / distanceToMeters,
									jsonArray[j][2] / distanceToMeters
								);
								var tDistance = checkDistance(vertex, earthCenter);
								if (tDistance < earthSafeZone) {
									var newT = updateDistance(vertex, tDistance);
									vertex.x = newT.x;
									vertex.y = newT.y;
									vertex.z = newT.z;
								}
								verticesArray.push(vertex);
							}

							// Drop lagging points behind the live vehicle; keep forward path
							verticesArray = trimDragonTrajectoryToVehicle(verticesArray, vehicleMesh.position);

							if (!verticesArray || verticesArray.length < 2) {
								if (dragonTrajectoryObjects[id]) {
									dragonTrajectoryObjects[id].visible = false;
								}
								delete dragonTrajectoryVertices[id];
							} else {
								dragonTrajectoryVertices[id] = verticesArray;

								if (!dragonTrajectoryObjects[id]) {
									var trajLineTotal = verticesArray.length;
									var trajPositions = new Float32Array(trajLineTotal * 3);
									var trajAlphas = new Float32Array( trajLineTotal );
									var tempOpacity = 1;
									var opacityFadeFactor = trajLineTotal / 2;
									var opacityFadePoint = trajLineTotal - opacityFadeFactor;
									for (var m = 0; m < trajLineTotal; m++) {
										trajPositions[m * 3] = verticesArray[m].x;
										trajPositions[m * 3 + 1] = verticesArray[m].y;
										trajPositions[m * 3 + 2] = verticesArray[m].z;
										if ( m > opacityFadePoint ) {
											tempOpacity = 1 - (m - opacityFadePoint) / opacityFadeFactor;
										}
										trajAlphas[ m ] = tempOpacity;
									}
									var trajBufferGeometry = new THREE.BufferGeometry();
									trajBufferGeometry.setAttribute( 'position', new THREE.BufferAttribute( trajPositions, 3 ) );
									trajBufferGeometry.setAttribute( 'alpha', new THREE.BufferAttribute( trajAlphas, 1 ) );
									var trajShaderUniforms = {
										color: { value: vehicleTrajectoryColor },
									};
									var trajShaderMaterial = new THREE.ShaderMaterial( {
										uniforms: trajShaderUniforms,
										vertexShader:   $('#line_vertexshader').textContent,
										fragmentShader: $('#line_fragmentshader').textContent,
										transparent:    true
									});
									var trajectoryMesh = new THREE.Line( trajBufferGeometry, trajShaderMaterial );
									trajectoryMesh.visible = true;
									vehiclesObject.add( trajectoryMesh );
									dragonTrajectoryObjects[id] = trajectoryMesh;
								}
								var mesh = dragonTrajectoryObjects[id];
								var trajLineTotal = verticesArray.length;
								var currentCount = mesh.geometry.attributes.position.count;
								if (currentCount !== trajLineTotal) {
									var trajPositions = new Float32Array(trajLineTotal * 3);
									var trajAlphas = new Float32Array( trajLineTotal );
									var tempOpacity = 1;
									var opacityFadeFactor = trajLineTotal / 2;
									var opacityFadePoint = trajLineTotal - opacityFadeFactor;
									for (var m = 0; m < trajLineTotal; m++) {
										trajPositions[m * 3] = verticesArray[m].x;
										trajPositions[m * 3 + 1] = verticesArray[m].y;
										trajPositions[m * 3 + 2] = verticesArray[m].z;
										if ( m > opacityFadePoint ) {
											tempOpacity = 1 - (m - opacityFadePoint) / opacityFadeFactor;
										}
										trajAlphas[ m ] = tempOpacity;
									}
									mesh.geometry.setAttribute( 'position', new THREE.BufferAttribute( trajPositions, 3 ) );
									mesh.geometry.setAttribute( 'alpha', new THREE.BufferAttribute( trajAlphas, 1 ) );
								} else {
									var positions = mesh.geometry.attributes.position.array;
									for (var i = 0; i < trajLineTotal; i++) {
										positions[i * 3] = verticesArray[i].x;
										positions[i * 3 + 1] = verticesArray[i].y;
										positions[i * 3 + 2] = verticesArray[i].z;
									}
									mesh.geometry.attributes.position.needsUpdate = true;
								}
								mesh.visible = (id === featuredVehicle);
							}
						} else {
							if (dragonTrajectoryObjects[id]) {
								dragonTrajectoryObjects[id].visible = false;
							}
							delete dragonTrajectoryVertices[id];
						}
					}

					// TELEMETRY FROM FEATURED
					if (featuredVehicle && vehicles[featuredVehicle]) {
						updateTelemetryFromVehicle(featuredVehicle)
					}

					for (var id in dragonVehicles) {
						var mesh = dragonVehicles[id];
						mesh.material.map = dragonTexture;
						mesh.visible = true;
					}

					// PROXIMITY TO ISS
					var proximityCount = 0;
					var hideIssDueToProximity = false;
					var dockedMeshes = [];
					for (var id in dragonVehicles) {
						var dragonMesh = dragonVehicles[id];
						if (dragonMesh.visible && issMesh.visible) {
							var proximity = checkDistance(dragonMesh.position, issMesh.position);
							if (proximity <= 400) {
								proximityCount++;
								hideIssDueToProximity = true;
								dockedMeshes.push(dragonMesh);
							}
						}
					}

					// SHOW UP TO TWO DRAGONS AT DOCKED AT THE ISS
					switch (proximityCount) {
						case 2:
							dockedMeshes[0].material.map = dragonIssTexture2;
							dockedMeshes[1].visible = false;
							break;
						case 1:
							dockedMeshes[0].material.map = dragonIssTexture;
							break;
					}

					if (hideIssDueToProximity) {
						hideISS();
					}
					if (window.onTrackerUpdate) window.onTrackerUpdate();
				} else {
					// NO VEHICLES
					for (var id in dragonVehicles) {
						dragonVehicles[id].visible = false;
						if (dragonTrajectoryObjects[id]) {
							dragonTrajectoryObjects[id].visible = false;
						}
					}

					hideISS();
					if (Object.keys(starshipData).length === 0) {
						hideVehicleTelemetry();
					}
					featuredVehicle = null;
					window.featuredVehicle = null;
					var vehiclesDiv = $('#vehicles');
					vehiclesDiv.innerHTML = '';
					if (window.onTrackerUpdate) window.onTrackerUpdate();
				}
			} else {
				// error
				for (var id in dragonVehicles) {
					dragonVehicles[id].visible = false;
					if (dragonTrajectoryObjects[id]) {
						dragonTrajectoryObjects[id].visible = false;
					}
				}
				hideISS();

				if (Object.keys(starshipData).length === 0) {
					hideVehicleTelemetry();
				}
				featuredVehicle = null;
				var vehiclesDiv = $('#vehicles');
				vehiclesDiv.innerHTML = '';
				if (window.onTrackerUpdate) window.onTrackerUpdate();
			}
		}
		request.send();
	}

	function starshipTrackerLoop() {
		var request = new XMLHttpRequest();
		request.open('GET', (frozenServices ? serviceUrls.snapshots["starship_tracker_public.json"] : serviceUrls.live["starship_tracker_public.json"]) + "?" + new Date().getTime(), true);
		//request.open('GET', './assets/json/vehicle-tracker/starship_sample.json?'+ new Date().getTime(), true);
		request.onload = function() {
			if (this.status >= 200 && this.status < 400) {
				var data = JSON.parse(this.response);
				if (data) {
					starshipData = data;
					setCurrentVehicles();
					var vehicles = data;
					var vehicleIds = Object.keys(vehicles).filter(function(id) { return id !== "metadata"; });

					// REMOVE OLD STARSHIP VEHICLES IF NOT IN CURRENT
					for (var id in starshipVehicles) {
						if (vehicleIds.indexOf(id) === -1) {
							vehiclesObject.remove(starshipVehicles[id]);
							if (starshipTrajectoryObjects[id]) {
								vehiclesObject.remove(starshipTrajectoryObjects[id]);
							}
							delete starshipVehicles[id];
							delete starshipTrajectoryObjects[id];
							delete starshipTrajectoryVertices[id];
							delete allMeshes[id];
						}
					}

					// PROCESS VEHICLES
					for (var k = 0; k < vehicleIds.length; k++) {
						var id = vehicleIds[k];
						var vData = vehicles[id];
						// create if not exist
						if (!starshipVehicles[id]) {
							var vehicleMaterial = new THREE.MeshBasicMaterial( {
								map: starshipTexture,
								transparent: true,
								opacity: 0,
								side: THREE.DoubleSide,
								depthWrite: false
							});
							vehicleMaterial.needsUpdate = true;
							var vehicleGeometry = new THREE.PlaneGeometry( iconSize, iconSize, 32 );
							var vehicleMesh = new THREE.Mesh( vehicleGeometry, vehicleMaterial );
							vehicleMesh.visible = false;
							var tempIconSize = iconSize;
							if (deviceSettings.isMobile) {
								tempIconSize = iconSize * 2;
							}
							vehicleMesh.scale.set( tempIconSize, tempIconSize, tempIconSize );
							vehicleMesh.position.set( 0, 0, 0 );
							vehiclesObject.add(vehicleMesh);
							starshipVehicles[id] = vehicleMesh;
							allMeshes[id] = vehicleMesh;
						}
						var vehicleMesh = starshipVehicles[id];
						var vehicleMaterial = vehicleMesh.material;

						// UPDATE POSITIONS
						if (vData["current"]["r_ecef"]) {
							var px = vData["current"]["r_ecef"][0] / distanceToMeters;
							var py = vData["current"]["r_ecef"][1] / distanceToMeters;
							var pz = vData["current"]["r_ecef"][2] / distanceToMeters;
							var pVertex = new THREE.Vector3(px, py, pz);
							var pDistance = checkDistance(pVertex, earthCenter);
							if (pDistance < earthSafeZone) {
								var newPosition = updateDistance(pVertex, pDistance);
								px = newPosition.x;
								py = newPosition.y;
								pz = newPosition.z;
							}
							vehicleMesh.position.set( px, py, pz );
							if (vehicleMesh.visible === false) {
								vehicleMesh.visible = true;
								gsap.fromTo( vehicleMaterial, 1, { opacity: 0 }, { opacity: 1 });
							}
							if (id === featuredVehicle && !isRotated) {
								rotateToLocation(px, py, pz);
							}
						} else {
							vehicleMesh.visible = false;
						}

						// UPDATE TRAJECTORIES
						if (vData["trajectory"]) {
							var jsonArray = vData["trajectory"].map(function(t) { return t["r_ecef"]; });
							var verticesArray = [];
							for (var j = 0; j < jsonArray.length; j++) {
								var vertex = new THREE.Vector3(
									jsonArray[j][0] / distanceToMeters,
									jsonArray[j][1] / distanceToMeters,
									jsonArray[j][2] / distanceToMeters
								);
								var tDistance = checkDistance(vertex, earthCenter);
								if (tDistance < earthSafeZone) {
									var newT = updateDistance(vertex, tDistance);
									vertex.x = newT.x;
									vertex.y = newT.y;
									vertex.z = newT.z;
								}
								verticesArray.push(vertex);
							}

							starshipTrajectoryVertices[id] = verticesArray;

							if (!starshipTrajectoryObjects[id]) {
								var trajLineTotal = verticesArray.length;
								var trajPositions = new Float32Array(trajLineTotal * 3);
								var trajAlphas = new Float32Array( trajLineTotal );
								var tempOpacity = 1;
								var opacityFadeFactor = trajLineTotal / 2;
								var opacityFadePoint = trajLineTotal - opacityFadeFactor;
								for (var m = 0; m < trajLineTotal; m++) {
									trajPositions[m * 3] = verticesArray[m].x;
									trajPositions[m * 3 + 1] = verticesArray[m].y;
									trajPositions[m * 3 + 2] = verticesArray[m].z;
									if ( m > opacityFadePoint ) {
										tempOpacity = 1 - (m - opacityFadePoint) / opacityFadeFactor;
									}
									trajAlphas[ m ] = tempOpacity;
								}
								var trajBufferGeometry = new THREE.BufferGeometry();
								trajBufferGeometry.setAttribute( 'position', new THREE.BufferAttribute( trajPositions, 3 ) );
								trajBufferGeometry.setAttribute( 'alpha', new THREE.BufferAttribute( trajAlphas, 1 ) );
								var trajShaderUniforms = {
									color: { value: vehicleTrajectoryColor },
								};
								var trajShaderMaterial = new THREE.ShaderMaterial( {
									uniforms: trajShaderUniforms,
									vertexShader:   $('#line_vertexshader').textContent,
									fragmentShader: $('#line_fragmentshader').textContent,
									transparent:    true
								});
								var trajectoryMesh = new THREE.Line( trajBufferGeometry, trajShaderMaterial );
								trajectoryMesh.visible = true;
								vehiclesObject.add( trajectoryMesh );
								starshipTrajectoryObjects[id] = trajectoryMesh;
							}
							var mesh = starshipTrajectoryObjects[id];
							var trajLineTotal = verticesArray.length;
							var currentCount = mesh.geometry.attributes.position.count;
							if (currentCount !== trajLineTotal) {
								var trajPositions = new Float32Array(trajLineTotal * 3);
								var trajAlphas = new Float32Array( trajLineTotal );
								var tempOpacity = 1;
								var opacityFadeFactor = trajLineTotal / 2;
								var opacityFadePoint = trajLineTotal - opacityFadeFactor;
								for (var m = 0; m < trajLineTotal; m++) {
									trajPositions[m * 3] = verticesArray[m].x;
									trajPositions[m * 3 + 1] = verticesArray[m].y;
									trajPositions[m * 3 + 2] = verticesArray[m].z;
									if ( m > opacityFadePoint ) {
										tempOpacity = 1 - (m - opacityFadePoint) / opacityFadeFactor;
									}
									trajAlphas[ m ] = tempOpacity;
								}
								mesh.geometry.setAttribute( 'position', new THREE.BufferAttribute( trajPositions, 3 ) );
								mesh.geometry.setAttribute( 'alpha', new THREE.BufferAttribute( trajAlphas, 1 ) );
							} else {
								var positions = mesh.geometry.attributes.position.array;
								for (var i = 0; i < trajLineTotal; i++) {
									positions[i * 3] = verticesArray[i].x;
									positions[i * 3 + 1] = verticesArray[i].y;
									positions[i * 3 + 2] = verticesArray[i].z;
								}
								mesh.geometry.attributes.position.needsUpdate = true;
							}
							mesh.visible = (id === featuredVehicle) && (vData["current"]["altitude"] >= 500);
						} else {
							if (starshipTrajectoryObjects[id]) {
								starshipTrajectoryObjects[id].visible = false;
							}
							delete starshipTrajectoryVertices[id];
						}
					}

					// TELEMETRY FROM FEATURED
					if (featuredVehicle && vehicles[featuredVehicle]) {
						updateTelemetryFromVehicle(featuredVehicle)
					}
					if (window.onTrackerUpdate) window.onTrackerUpdate();
				}
			}
		};
		request.send();
	}

	function setFeatured(id) {
		isRotated = false;
		featuredVehicle = id;
		window.featuredVehicle = id;
		for (var oid in dragonTrajectoryObjects) {
			dragonTrajectoryObjects[oid].visible = (oid === id);
		}
		for (var oid in starshipTrajectoryObjects) {
			var visible = (oid === id);
			if (visible && window.currentVehicles[oid] && window.currentVehicles[oid]["current"]["altitude"] < 500) {
				visible = false;
			}
			starshipTrajectoryObjects[oid].visible = visible;
		}
	}

	function showISS() {
		if (issCreated) {
			issMesh.visible = true;
		}
	}

	function hideISS() {
		if (issCreated) {
			issMesh.visible = false;
		}
	}

	function hideVehicleTelemetry() {
		if (vehicleTelemetryCreated) {
			//$('#telemetry').style.display = 'none';
			$('#telemetry').style.opacity = 0;
		}
	}

	function updateTelemetryFromVehicle(id) {
		if (window.currentVehicles[id]) {
			var vData = window.currentVehicles[id];
			var missionTime, speed, alt;
			if (vData["glass.dragon.mission_time_f64"] !== undefined && vData["glass.dgn_speed_f64"] !== undefined && vData["glass.dgn_alt_geod_f64"] !== undefined) {
				missionTime = vData["glass.dragon.mission_time_f64"];
				speed = vData["glass.dgn_speed_f64"];
				alt = vData["glass.dgn_alt_geod_f64"];
			} else if (vData["current"] && vData["current"]["mission_time"] !== undefined && vData["current"]["speed"] !== undefined && vData["current"]["altitude"] !== undefined) {
				missionTime = vData["current"]["mission_time"];
				speed = vData["current"]["speed"];
				alt = vData["current"]["altitude"];
			} else {
				//hideVehicleTelemetry();
				return;
			}
			vehicleTelemetryTime = formatTime(missionTime);
			vehicleTelemetrySpeed = parseInt(speed * 3.6);
			vehicleTelemetryAltitude = parseInt(alt / 1000);

			// These numbers came from discussions with GNC.
			if (vehicleTelemetrySpeed < 0 || vehicleTelemetrySpeed > 40000) {
				vehicleTelemetrySpeed = 0;
			}
			if (vehicleTelemetryAltitude < 0 || vehicleTelemetryAltitude > 2000) {
				vehicleTelemetryAltitude = 0;
			}
			if (vehicleTelemetrySpeed == 0 && vehicleTelemetryAltitude == 0) {
				vehicleTelemetryTime = "0D 00:00";
			}
			vehicleTelemetrySpeed = addComma(vehicleTelemetrySpeed);
			if (!vehicleTelemetryCreated) {
				showVehicleTelemetry();
			}
		} else {
			hideVehicleTelemetry();
		}
	}

	function formatTime(totalSeconds) {
		const days = Math.floor(totalSeconds / (24 * 3600));
		const hours = Math.floor((totalSeconds % (24 * 3600)) / 3600);
		const minutes = Math.floor((totalSeconds % 3600) / 60);
		const seconds = totalSeconds % 60;

		const formattedDays = String(days).padStart(1, '0');
		const formattedHours = String(hours).padStart(2, '0');
		const formattedMinutes = String(minutes).padStart(2, '0');
		//const formattedSeconds = String(seconds).padStart(2, '0');

		return formattedDays + "D " + formattedHours + ":" + formattedMinutes;
	}

	function addComma(number) {
		return number.toLocaleString();
	}

	function checkDistance(object, center) {
		return object.distanceTo(center);
	}

	function updateDistance(objectVertex, distance) {
		var direction = objectVertex.clone().normalize();
		var safeDistance = objectVertex.clone().addScaledVector(direction, (earthSafeZone - distance));
		return new THREE.Vector3(safeDistance.x, safeDistance.y, safeDistance.z);
	}

	function rotateToLocation(x, y, z) {
		var localPos = new THREE.Vector3(x, y, z);
		localPos.applyMatrix4(vehiclesObject.matrix);
		var dir = localPos.clone().normalize();
		var newRotationY = -Math.atan2(dir.x, dir.z);
		var newRotationX = Math.asin(dir.y);
		targetRotationY = newRotationY;
		targetRotationX = newRotationX;
	}

	// ANIMATIONS & RENDERING
	function animate() {
		requestAnimationFrame( animate );
		render();
	}

	function render() {
		renderer.render( scene, camera );

		renderISS();
		renderDragonVehicles();
		renderStarshipVehicles();
		renderVehicleTelemetry();

		if (isEventsEnabled) {
			if (targetRotationX > 90 * toRAD) targetRotationX = 90 * toRAD;
			if (targetRotationX < -90 * toRAD) targetRotationX = -90 * toRAD;
			rotationObject.rotation.x = rotationObject.rotation.x += ( targetRotationX - rotationObject.rotation.x ) * dragSpeed;
			rotationObject.rotation.y = rotationObject.rotation.y += ( targetRotationY - rotationObject.rotation.y ) * dragSpeed;
		}
	}

	// MOUSE AND MOUSE WHEEL
	function onMouseWheel( event ) {
		event.preventDefault();
		targetCameraZ -= event.wheelDeltaY * 0.01;
	}

	function onDocumentMouseDown( event ) {
		if ( isEventsEnabled === false ) return;
		event.preventDefault();
		isMouseDown = true;

		mouseXOnMouseDown = event.clientX - windowHalfX;
		mouseYOnMouseDown = event.clientY - windowHalfY;

		targetRotationXOnMouseDown = targetRotationX;
		targetRotationYOnMouseDown = targetRotationY;

		initMouseX = event.clientX;
	}

	function onDocumentMouseMove( event ) {
		if ( isEventsEnabled === false ) return;
		isMouseMoved = true;
		clientMouseX = event.clientX;
		clientMouseY = event.clientY;

		mouse.x = ( event.clientX / window.innerWidth ) * 2 - 1;
		mouse.y = - ( event.clientY / window.innerHeight ) * 2 + 1;

		if (isMouseDown) {
			isRotated = true;
			mouseX = event.clientX - windowHalfX;
			mouseY = event.clientY - windowHalfY;
			targetRotationX = targetRotationXOnMouseDown + ( mouseY - mouseYOnMouseDown ) * 0.0025;
			targetRotationY = targetRotationYOnMouseDown + ( mouseX - mouseXOnMouseDown ) * 0.0025;
		}
	}

	function onDocumentMouseUp( event ) {
		if ( isEventsEnabled === false ) return;
		event.preventDefault();
		isMouseDown = false;
	}

	function onDocumentMouseLeave( event ) {
		if ( isEventsEnabled === false ) return;
		event.preventDefault();
		if (isMouseDown) {
			isMouseDown = false;
		}
	}

	// TOUCH
	var _touchZoomDistanceStart,
		_touchZoomDistanceEnd;
	function onDocumentTouchStart( event ) {
		if ( isEventsEnabled === false ) return;
		if ( event.touches.length == 1 ) {
			event.preventDefault();
			isMouseDown = true;

			mouseXOnMouseDown = event.touches[ 0 ].pageX - windowHalfX;
			mouseYOnMouseDown = event.touches[ 0 ].pageY - windowHalfY;

			targetRotationXOnMouseDown = targetRotationX;
			targetRotationYOnMouseDown = targetRotationY;

			mouse.x = (event.changedTouches[0].clientX / window.innerWidth) * 2 - 1;
			mouse.y = -(event.changedTouches[0].clientY / window.innerHeight) * 2 + 1;
		}

		if ( event.touches.length > 1 ) {
			var dx = event.touches[ 0 ].pageX - event.touches[ 1 ].pageX;
			var dy = event.touches[ 0 ].pageY - event.touches[ 1 ].pageY;
			_touchZoomDistanceEnd = _touchZoomDistanceStart = Math.sqrt( dx * dx + dy * dy );
		}
	}

	function onDocumentTouchMove( event ) {
		if ( isEventsEnabled === false ) return;
		if ( event.touches.length == 1 ) {
			event.preventDefault();
			if (isMouseDown) {
				isRotated = true;
				mouseX = mouseX = event.touches[ 0 ].pageX - windowHalfX;
				mouseY = mouseY = event.touches[ 0 ].pageY - windowHalfY;
				// TURNING OFF UP/DOWN FOR NOW
				targetRotationX = targetRotationXOnMouseDown + ( mouseY - mouseYOnMouseDown ) * 0.005;
				targetRotationY = targetRotationYOnMouseDown + ( mouseX - mouseXOnMouseDown ) * 0.005;
			}
		}
	}

	function onDocumentTouchEnd( event ) {
		_touchZoomDistanceStart = _touchZoomDistanceEnd = 0;
		onDocumentMouseUp(event);
	}

	// RESIZE
	function onWindowResize() {
		width = window.innerWidth;
		height = window.innerHeight;

		// RESPONSIVE CANVAS HEIGHT
		if (width < 1000) {
			height = width;

			// CENTER THE CAMERA
			if (rotationObject) {
				rotationObject.position.x = 0;
			}
		} else {
			// PUT THE CAMERA BACK
			if (rotationObject) {
				rotationObject.position.x = baseCameraX;
			}
		}

		// Webcast wants a centered scene.
		if (webcast) {
			if (rotationObject) {
				rotationObject.position.x = 0;
			}
		}

		camera.aspect = width / height;
		camera.updateProjectionMatrix();
		renderer.setSize( width, height );
	}

	if ( WEBGL.isWebGLAvailable() ) {
		deviceSettings.isWebGL = true;
		initWebgl();
	} else {
		var warning = WEBGL.getWebGLErrorMessage();
		$('#interactive').appendChild( warning );
	}

	// Expose for Angular integration
	window.setFeatured = setFeatured;
	window.rotateToLocation = rotateToLocation;
	window.updateTelemetryFromVehicle = updateTelemetryFromVehicle;
	window.vehicles = allMeshes;
	window.currentVehicles = currentVehicles;
	window.featuredVehicle = featuredVehicle;
	window.isRotated = isRotated;
})();