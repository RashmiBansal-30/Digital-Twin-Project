/**
 * AeroEngine3D - Professional Cutaway Inline-4 DOHC Aero Piston Engine Model
 *
 * Features:
 * - High-Detail Mechanical Cutaway Inline 4-Cylinder DOHC Architecture
 * - Semi-Transparent Cutaway Cylinders exposing reciprocating pistons & valves
 * - 4-Throw Counterweighted Crankshaft, Flywheel & Timing Chain Drive
 * - Twin Overhead Camshafts (DOHC) with reciprocating poppet valves
 * - 1-3-4-2 Firing Sequence & Thermal Fault Glow Visualizer (Exact match to reference image)
 * - Interactive Component Inspection Mode & Cutaway View Toggle
 */

class AeroEngine3D {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    if (!this.container) {
      console.error(`Container #${containerId} not found for 3D engine.`);
      return;
    }

    this.onComponentSelect = options.onComponentSelect || null;

    this.currentRPM = 2800;
    this.isRunning = true;
    this.crankAngle = 0;
    this.explodedFactor = 0;
    this.targetExplodedFactor = 0;
    this.activeFault = 'Normal';
    this.vibrationLevel = 0.25;
    this.selectedMesh = null;

    this.components = {};
    this.componentData = {
      cylinders: {
        name: "Cutaway Cylinders & Combustion Chambers",
        purpose: "Houses the combustion chambers and contains gas pressure during power expansion strokes.",
        operation: "Semi-transparent sleeve provides a clear view of piston reciprocation and valve operation inside.",
        telemetry: "Cylinder Head Temperature (CHT), Exhaust Gas Temperature (EGT)",
        faultMeaning: "Elevated CHT (>190°C) causes thermal stress, cylinder wall scoring, and knocking."
      },
      pistons: {
        name: "Pistons & Wrist Pins",
        purpose: "Converts combustion gas pressure into linear mechanical force transferred to connecting rods.",
        operation: "Reciprocates vertically inside cylinder sleeves with piston rings maintaining gas compression seal.",
        telemetry: "Engine Speed (RPM), Engine Load %, CHT",
        faultMeaning: "Thermal expansion or oil starvation causes piston scuffing and wrist pin clearance play."
      },
      crankshaft: {
        name: "Counterweighted Crankshaft & Flywheel",
        purpose: "Converts reciprocating piston movement into smooth rotational torque to turn the UAV propeller.",
        operation: "4-throw offset crankpins with counterweights balance inertia. Large flywheel smooths torque pulses.",
        telemetry: "RPM, Structural Vibration (g)",
        faultMeaning: "High vibration (>0.5g) signals main bearing wear, shaft unbalance, or crankpin fatigue."
      },
      connectingRods: {
        name: "H-Beam Connecting Rods",
        purpose: "Links piston wrist pins directly to crankshaft crankpin journals.",
        operation: "Pivots laterally while reciprocating vertically as crankshaft rotates through 360 degrees.",
        telemetry: "RPM, Engine Load %, Vibration (g)",
        faultMeaning: "Rod bearing clearance play causes mechanical knocking and catastrophic fatigue failure."
      },
      camshafts: {
        name: "Dual Overhead Camshafts (DOHC) & Timing Chain",
        purpose: "Controls precise intake and exhaust valve opening and closing timing relative to crankshaft position.",
        operation: "Timing chain rotates twin camshafts at half crankshaft speed. Cam lobes depress poppet valves.",
        telemetry: "Engine Speed (RPM), Manifold Pressure",
        faultMeaning: "Cam lobe wear or timing chain stretch degrades volumetric efficiency and causes power loss."
      },
      valves: {
        name: "Intake & Exhaust Poppet Valves",
        purpose: "Seals combustion chamber during compression/power strokes and opens for intake/exhaust gas exchange.",
        operation: "Depressed by rotating cam lobes against return springs, extending down into top of cylinder head.",
        telemetry: "Exhaust Gas Temperature (EGT), Manifold Pressure",
        faultMeaning: "Burnt or sticking valves cause combustion leaks, misfiring, and erratic EGT spikes."
      }
    };

    this.initScene();
    this.buildEngineGeometry();
    this.setupLighting();
    this.setupInteractivity();
    this.animate();

    window.addEventListener('resize', () => this.onWindowResize());
  }

  initScene() {
    const width = this.container.clientWidth || 600;
    const height = this.container.clientHeight || 400;

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0a0e17);
    this.scene.fog = new THREE.FogExp2(0x0a0e17, 0.012);

    this.camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 1000);
    this.camera.position.set(22, 16, 26);

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    this.container.appendChild(this.renderer.domElement);

    if (typeof THREE.OrbitControls !== 'undefined') {
      this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
    } else if (typeof OrbitControls !== 'undefined') {
      this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    } else {
      this.controls = { update: () => {} };
    }

    if (this.controls.enableDamping !== undefined) {
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.05;
      this.controls.maxPolarAngle = Math.PI / 2 + 0.1;
      this.controls.minDistance = 10;
      this.controls.maxDistance = 60;
    }

    // Reflective Metallic Grid Floor
    const gridHelper = new THREE.GridHelper(60, 30, 0x38bdf8, 0x1e293b);
    gridHelper.position.y = -8;
    this.scene.add(gridHelper);
  }

  setupLighting() {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    this.scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 1.4);
    keyLight.position.set(25, 35, 20);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.width = 1024;
    keyLight.shadow.mapSize.height = 1024;
    this.scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x38bdf8, 0.6);
    fillLight.position.set(-20, 15, -20);
    this.scene.add(fillLight);

    const rimLight = new THREE.DirectionalLight(0xffffff, 0.8);
    rimLight.position.set(0, 20, -30);
    this.scene.add(rimLight);
  }

  buildEngineGeometry() {
    this.engineGroup = new THREE.Group();
    this.scene.add(this.engineGroup);

    // High-Quality Metallic PBR Materials
    this.matChrome = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.95, roughness: 0.15 });
    this.matSteel = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.85, roughness: 0.25 });
    this.matDarkMetal = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.8, roughness: 0.4 });
    this.matBrass = new THREE.MeshStandardMaterial({ color: 0xd97706, metalness: 0.9, roughness: 0.2 });

    // Cutaway Cylinder Sleeve Glass Material
    this.matGlass = new THREE.MeshPhysicalMaterial({
      color: 0x94a3b8,
      metalness: 0.2,
      roughness: 0.1,
      transmission: 0.8,
      opacity: 0.35,
      transparent: true,
      side: THREE.DoubleSide
    });

    // Cylinder Positions along Z-axis
    this.cylZPositions = [-7.5, -2.5, 2.5, 7.5];

    // 1. Cutaway Cylinders (4 Units)
    this.cylindersGroup = new THREE.Group();
    this.cylinderMeshes = [];
    this.combustionLights = [];
    this.combustionMeshes = [];

    this.cylZPositions.forEach((zPos, idx) => {
      // Cylinder Sleeve Outer Cutaway Tube
      const sleeveGeo = new THREE.CylinderGeometry(2.4, 2.4, 8, 32, 1, true, Math.PI * 0.15, Math.PI * 1.7);
      const sleeveMesh = new THREE.Mesh(sleeveGeo, this.matGlass);
      sleeveMesh.position.set(0, 4, zPos);
      sleeveMesh.userData = { type: 'cylinders', key: 'cylinders', id: idx };
      this.cylindersGroup.add(sleeveMesh);
      this.cylinderMeshes.push(sleeveMesh);

      // Top Cylinder Head Cap
      const headCapGeo = new THREE.CylinderGeometry(2.5, 2.5, 1.2, 32);
      const headCapMesh = new THREE.Mesh(headCapGeo, this.matSteel);
      headCapMesh.position.set(0, 8.2, zPos);
      headCapMesh.userData = { type: 'cylinders', key: 'cylinders', id: idx };
      this.cylindersGroup.add(headCapMesh);

      // Inner Combustion Chamber Glow Volume
      const combGeo = new THREE.CylinderGeometry(2.2, 2.2, 2.5, 24);
      const combMat = new THREE.MeshBasicMaterial({ color: 0xffaa00, transparent: true, opacity: 0.0 });
      const combMesh = new THREE.Mesh(combGeo, combMat);
      combMesh.position.set(0, 6.8, zPos);
      this.cylindersGroup.add(combMesh);
      this.combustionMeshes.push(combMesh);

      // Combustion Point Light
      const combLight = new THREE.PointLight(0xffaa00, 0, 12);
      combLight.position.set(0, 6.8, zPos);
      this.cylindersGroup.add(combLight);
      this.combustionLights.push(combLight);
    });

    this.engineGroup.add(this.cylindersGroup);
    this.components.cylinders = this.cylindersGroup;

    // 2. Heavy Counterweighted Crankshaft & Flywheel Assembly
    this.crankshaftGroup = new THREE.Group();
    this.crankshaftGroup.position.set(0, -3, 0);

    // Main Center Shaft
    const mainShaftGeo = new THREE.CylinderGeometry(0.7, 0.7, 20, 24);
    const mainShaftMesh = new THREE.Mesh(mainShaftGeo, this.matChrome);
    mainShaftMesh.rotation.x = Math.PI / 2;
    this.crankshaftGroup.add(mainShaftMesh);

    // Crankpins & Counterweights (4 Throws - 180° Flat Plane)
    // Cyl 1 (0°), Cyl 2 (180°), Cyl 3 (180°), Cyl 4 (0°)
    this.crankPhases = [0, Math.PI, Math.PI, 0];
    this.crankpinMeshes = [];

    this.cylZPositions.forEach((zPos, idx) => {
      const phase = this.crankPhases[idx];
      const radius = 2.0;

      // Crankpin Journal
      const pinGeo = new THREE.CylinderGeometry(0.6, 0.6, 1.4, 20);
      const pinMesh = new THREE.Mesh(pinGeo, this.matChrome);
      pinMesh.position.set(radius * Math.sin(phase), radius * Math.cos(phase), zPos);
      pinMesh.rotation.x = Math.PI / 2;
      pinMesh.userData = { type: 'crankshaft', key: 'crankshaft' };
      this.crankshaftGroup.add(pinMesh);
      this.crankpinMeshes.push(pinMesh);

      // Counterweight Lobes (2 per cylinder throw)
      [-0.9, 0.9].forEach(offset => {
        const cwGeo = new THREE.CylinderGeometry(2.6, 2.6, 0.5, 24, 1, false, Math.PI * 0.75, Math.PI * 1.5);
        const cwMesh = new THREE.Mesh(cwGeo, this.matChrome);
        cwMesh.position.set(-radius * 0.6 * Math.sin(phase), -radius * 0.6 * Math.cos(phase), zPos + offset);
        cwMesh.rotation.z = phase + Math.PI;
        cwMesh.userData = { type: 'crankshaft', key: 'crankshaft' };
        this.crankshaftGroup.add(cwMesh);
      });
    });

    // Flywheel (Left End, z = -11)
    const flywheelGeo = new THREE.CylinderGeometry(5.5, 5.5, 0.8, 48);
    const flywheelMesh = new THREE.Mesh(flywheelGeo, this.matSteel);
    flywheelMesh.position.set(0, 0, -11);
    flywheelMesh.rotation.x = Math.PI / 2;
    flywheelMesh.userData = { type: 'crankshaft', key: 'crankshaft' };
    this.crankshaftGroup.add(flywheelMesh);

    // Flywheel Outer Ring Gear Teeth
    const ringGeo = new THREE.TorusGeometry(5.6, 0.25, 16, 60);
    const ringMesh = new THREE.Mesh(ringGeo, this.matChrome);
    ringMesh.position.set(0, 0, -11);
    this.crankshaftGroup.add(ringMesh);

    // Timing Sprocket (Right End, z = 10.5)
    const sprocketGeo = new THREE.CylinderGeometry(1.8, 1.8, 0.5, 24);
    const sprocketMesh = new THREE.Mesh(sprocketGeo, this.matDarkMetal);
    sprocketMesh.position.set(0, 0, 10.5);
    sprocketMesh.rotation.x = Math.PI / 2;
    this.crankshaftGroup.add(sprocketMesh);

    this.engineGroup.add(this.crankshaftGroup);
    this.components.crankshaft = this.crankshaftGroup;

    // 3. Pistons & H-Beam Connecting Rods
    this.pistons = [];
    this.rods = [];

    this.cylZPositions.forEach((zPos, idx) => {
      const phase = this.crankPhases[idx];

      // Piston
      const pistonGeo = new THREE.CylinderGeometry(2.2, 2.2, 2.8, 32);
      const pistonMesh = new THREE.Mesh(pistonGeo, this.matSteel);
      pistonMesh.position.set(0, 4, zPos);
      pistonMesh.userData = { type: 'pistons', key: 'pistons', id: idx };

      // Piston Ring Grooves
      [-0.6, 0.0, 0.6].forEach(yRing => {
        const ringGeo = new THREE.TorusGeometry(2.22, 0.04, 8, 32);
        const ringMesh = new THREE.Mesh(ringGeo, this.matChrome);
        ringMesh.position.set(0, yRing, 0);
        ringMesh.rotation.x = Math.PI / 2;
        pistonMesh.add(ringMesh);
      });

      this.engineGroup.add(pistonMesh);

      // Connecting Rod
      const rodGroup = new THREE.Group();
      const rodBodyGeo = new THREE.BoxGeometry(0.6, 5.2, 0.5);
      const rodBodyMesh = new THREE.Mesh(rodBodyGeo, this.matChrome);
      rodGroup.add(rodBodyMesh);

      // Lower Rod Big-End Cap
      const capGeo = new THREE.CylinderGeometry(1.0, 1.0, 0.6, 20);
      const capMesh = new THREE.Mesh(capGeo, this.matChrome);
      capMesh.position.set(0, -2.6, 0);
      capMesh.rotation.x = Math.PI / 2;
      rodGroup.add(capMesh);

      rodGroup.position.set(0, 1, zPos);
      rodGroup.userData = { type: 'connectingRods', key: 'connectingRods', id: idx };
      this.engineGroup.add(rodGroup);

      this.pistons.push({ mesh: pistonMesh, zPos, phase });
      this.rods.push({ group: rodGroup, zPos, phase });
    });

    this.components.pistons = this.pistons;
    this.components.connectingRods = this.rods;

    // 4. Dual Overhead Camshafts (DOHC) & Valves Assembly
    this.dohcGroup = new THREE.Group();
    this.dohcGroup.position.set(0, 11, 0);

    this.camshafts = [];
    this.valves = [];

    // 2 Camshafts (Intake x = -1.2, Exhaust x = 1.2)
    [-1.2, 1.2].forEach((xCam, camIdx) => {
      const camShaftGeo = new THREE.CylinderGeometry(0.5, 0.5, 20, 20);
      const camShaftMesh = new THREE.Mesh(camShaftGeo, this.matChrome);
      camShaftMesh.position.set(xCam, 0, 0);
      camShaftMesh.rotation.x = Math.PI / 2;
      this.dohcGroup.add(camShaftMesh);

      // Cam Sprocket (Right End, z = 10.5)
      const camSprocketGeo = new THREE.CylinderGeometry(2.5, 2.5, 0.4, 24);
      const camSprocketMesh = new THREE.Mesh(camSprocketGeo, this.matDarkMetal);
      camSprocketMesh.position.set(xCam, 0, 10.5);
      camSprocketMesh.rotation.x = Math.PI / 2;
      this.dohcGroup.add(camSprocketMesh);

      this.camshafts.push(camShaftMesh);

      // Cam Lobes & Poppet Valves per cylinder
      this.cylZPositions.forEach((zPos, cylIdx) => {
        const phase = this.crankPhases[cylIdx] * 0.5; // Camshaft turns at 1/2 crankshaft speed

        // Egg-Shaped Cam Lobe
        const lobeGeo = new THREE.CylinderGeometry(0.8, 0.5, 0.6, 16);
        const lobeMesh = new THREE.Mesh(lobeGeo, this.matChrome);
        lobeMesh.position.set(xCam, 0, zPos);
        lobeMesh.rotation.x = Math.PI / 2;
        this.dohcGroup.add(lobeMesh);

        // Poppet Valve (Stem + Tulip Head)
        const valveGroup = new THREE.Group();
        const stemGeo = new THREE.CylinderGeometry(0.12, 0.12, 3.2, 12);
        const stemMesh = new THREE.Mesh(stemGeo, this.matChrome);
        valveGroup.add(stemMesh);

        const tulipGeo = new THREE.CylinderGeometry(0.12, 0.7, 0.4, 16);
        const tulipMesh = new THREE.Mesh(tulipGeo, this.matChrome);
        tulipMesh.position.set(0, -1.6, 0);
        valveGroup.add(tulipMesh);

        valveGroup.position.set(xCam, -2.0, zPos);
        valveGroup.userData = { type: 'valves', key: 'valves', cylIdx, camIdx };
        this.dohcGroup.add(valveGroup);

        this.valves.push({ group: valveGroup, basePosY: -2.0, cylIdx, camIdx, phase });
      });
    });

    // Timing Chain (Right End connecting crankshaft sprocket to DOHC sprockets)
    const chainPath = new THREE.BoxGeometry(0.3, 11, 0.2);
    const chainMesh = new THREE.Mesh(chainPath, this.matDarkMetal);
    chainMesh.position.set(0, 4, 10.5);
    this.engineGroup.add(chainMesh);

    this.engineGroup.add(this.dohcGroup);
    this.components.camshafts = this.dohcGroup;
  }

  setupInteractivity() {
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();

    this.renderer.domElement.addEventListener('click', (event) => {
      const rect = this.renderer.domElement.getBoundingClientRect();
      this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      this.raycaster.setFromCamera(this.mouse, this.camera);
      const intersects = this.raycaster.intersectObjects(this.engineGroup.children, true);

      if (intersects.length > 0) {
        let hit = intersects[0].object;
        while (hit && hit !== this.engineGroup && (!hit.userData || !hit.userData.key)) {
          hit = hit.parent;
        }
        if (hit && hit.userData && hit.userData.key) {
          this.selectComponent(hit.userData.key, hit);
        }
      }
    });
  }

  selectComponent(key, mesh) {
    this.selectedMesh = mesh;
    const data = this.componentData[key];
    if (data && typeof this.onComponentSelect === 'function') {
      this.onComponentSelect(data);
    }
  }

  toggleExplodedView() {
    this.targetExplodedFactor = this.targetExplodedFactor === 0 ? 1 : 0;
  }

  updateRPM(rpm, isRunning, speedMultiplier = 1.0) {
    this.currentRPM = rpm;
    this.isRunning = isRunning;
    this.speedMultiplier = speedMultiplier;
  }

  updateFaultState(faultType, telemetry = {}, health = {}) {
    this.activeFault = faultType;
    const cht = telemetry.cylinder_head_temperature || 170;
    const oilPress = telemetry.oil_pressure || 4.2;
    const vib = telemetry.vibration || 0.25;

    // Reset default materials
    this.matSteel.emissive.setHex(0x000000);
    this.matChrome.emissive.setHex(0x000000);

    if (faultType === 'Overheating' || cht > 190) {
      // Overheating: Isolate & highlight Cylinder Heads, Combustion Chamber & Poppet Valves
      const thermalRatio = Math.min(1.0, Math.max(0.4, (cht - 170) / 50));

      this.combustionMeshes.forEach((mesh, idx) => {
        if (idx === 2 || idx === 1) { // Cyl 3 & 2 main overheating zones
          mesh.material.color.setHex(0xffaa00);
          mesh.material.opacity = 0.90 * thermalRatio;
          this.combustionLights[idx].color.setHex(0xffaa00);
          this.combustionLights[idx].intensity = 5.0 * thermalRatio;
        } else {
          mesh.material.opacity = 0.30 * thermalRatio;
          this.combustionLights[idx].intensity = 1.5 * thermalRatio;
        }
      });

    } else if (faultType === 'Lubrication Fault' || oilPress < 3.2) {
      // Lubrication Fault: Isolate & highlight Crankshaft Main Journals & Oil Sump
      this.matChrome.emissive.setHex(0xca8a04);
      this.matChrome.emissiveIntensity = 0.5;

      this.combustionMeshes.forEach((mesh, idx) => {
        mesh.material.color.setHex(0xeab308);
        mesh.material.opacity = 0.45;
        this.combustionLights[idx].color.setHex(0xeab308);
        this.combustionLights[idx].intensity = 3.0;
      });

    } else if (faultType === 'Mechanical/Vibration Fault' || vib > 0.45) {
      // Mechanical/Vibration Fault: Isolate & highlight Connecting Rods & Wrist Pins
      this.vibrationLevel = vib;
      this.matSteel.emissive.setHex(0xd97706);
      this.matSteel.emissiveIntensity = 0.6;

      this.combustionMeshes.forEach((mesh, idx) => {
        mesh.material.color.setHex(0xf97316);
        mesh.material.opacity = 0.55;
        this.combustionLights[idx].color.setHex(0xf97316);
        this.combustionLights[idx].intensity = 3.5;
      });

    } else {
      // Normal Operation: Reset static fault glow
      this.vibrationLevel = 0.25;
      this.combustionMeshes.forEach((mesh, idx) => {
        if (this.activeFault === 'Normal') {
          mesh.material.opacity = 0.0;
          this.combustionLights[idx].intensity = 0.0;
        }
      });
    }
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    const delta = 0.016; // ~60 FPS
    const speedMult = this.speedMultiplier || 1.0;

    // 1. Exploded View Transition
    this.explodedFactor += (this.targetExplodedFactor - this.explodedFactor) * 0.1;
    this.cylindersGroup.position.x = this.explodedFactor * 5;
    this.dohcGroup.position.y = 11 + (this.explodedFactor * 6);

    // 2. Kinematic Motion: Crankshaft, Pistons, Rods, Camshafts, Valves & 1-3-4-2 Firing Flash
    if (this.isRunning && this.currentRPM > 0) {
      const radPerSec = (this.currentRPM * 2 * Math.PI) / 60;
      this.crankAngle += radPerSec * delta * 0.12 * speedMult; // Scaled for smooth visual rendering

      // Rotate Crankshaft around Z-axis
      this.crankshaftGroup.rotation.z = this.crankAngle;

      // Rotate Camshafts at half speed
      this.dohcGroup.children.forEach(child => {
        if (child.geometry && child.geometry.type === 'CylinderGeometry') {
          child.rotation.z = this.crankAngle * 0.5;
        }
      });

      const stroke = 2.0;
      const baseCenterY = -3.0;
      const rodLength = 6.2;

      // Update Pistons and Connecting Rods
      this.pistons.forEach((p, i) => {
        const theta = this.crankAngle + p.phase;
        // Crankpin Y-position relative to crank center
        const pinY = baseCenterY + stroke * Math.cos(theta);
        const pinX = stroke * Math.sin(theta);

        // Piston position Y calculated via linkage geometry
        const pistonY = pinY + Math.sqrt(Math.max(0, rodLength * rodLength - pinX * pinX)) + 1.2;
        p.mesh.position.set(0, pistonY, p.zPos);

        // Connecting Rod
        const rod = this.rods[i];
        const midX = pinX * 0.5;
        const midY = (pinY + pistonY - 1.2) * 0.5;
        const angleZ = Math.atan2(-pinX, pistonY - 1.2 - pinY);

        rod.group.position.set(midX, midY, p.zPos);
        rod.group.rotation.z = angleZ;

        // 1-3-4-2 Sequential Ignition Flash during Normal Operation
        if (this.activeFault === 'Normal') {
          const normTheta = (theta % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2);
          if (normTheta < 0.4 || normTheta > (Math.PI * 2 - 0.4)) { // Top Dead Center (TDC) Power Stroke
            this.combustionMeshes[i].material.opacity = 0.85;
            this.combustionLights[i].intensity = 3.5;
          } else {
            this.combustionMeshes[i].material.opacity = 0.05;
            this.combustionLights[i].intensity = 0.2;
          }
        }
      });

      // Reciprocate Poppet Valves from Rotating Cam Lobes
      this.valves.forEach(v => {
        const camTheta = this.crankAngle * 0.5 + v.phase;
        const valLift = Math.max(0, Math.sin(camTheta)) * 0.8;
        v.group.position.y = v.basePosY - valLift;
      });
    }

    // 3. Vibration Motion Effect
    if (this.activeFault === 'Mechanical/Vibration Fault' || this.vibrationLevel > 0.45) {
      const vibAmp = Math.min(0.6, this.vibrationLevel * 0.12);
      this.engineGroup.position.x = (Math.random() - 0.5) * vibAmp;
      this.engineGroup.position.y = (Math.random() - 0.5) * vibAmp;
    } else {
      this.engineGroup.position.set(0, 0, 0);
    }

    if (this.controls && this.controls.update) {
      this.controls.update();
    }

    this.renderer.render(this.scene, this.camera);
  }

  onWindowResize() {
    if (!this.container) return;
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }
}

window.AeroEngine3D = AeroEngine3D;
