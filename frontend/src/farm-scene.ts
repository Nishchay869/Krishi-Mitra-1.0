import * as THREE from "three";

export function createFarmScene(host: HTMLElement): () => void {
  const renderer = new THREE.WebGLRenderer({
    alpha: true,
    antialias: false,
    powerPreference: "low-power",
  });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
  renderer.setClearColor(0x000000, 0);
  host.appendChild(renderer.domElement);
  host.classList.add("has-webgl");
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 50);
  camera.position.set(0, 1.5, 8);
  camera.lookAt(0, 0.6, 0);
  scene.add(new THREE.HemisphereLight(0xfff8d6, 0x5a713d, 2.4));
  const light = new THREE.DirectionalLight(0xffedb6, 3);
  light.position.set(-3, 4, 5);
  scene.add(light);
  const crop = new THREE.Group();
  const stemGeometry = new THREE.CylinderGeometry(0.025, 0.035, 2.5, 5);
  const grainGeometry = new THREE.SphereGeometry(0.12, 7, 5);
  const leafGeometry = new THREE.SphereGeometry(1, 7, 4);
  const stemMaterial = new THREE.MeshLambertMaterial({ color: 0x607d36 });
  const grainMaterial = new THREE.MeshLambertMaterial({ color: 0xd6af51 });
  const leafMaterial = new THREE.MeshLambertMaterial({ color: 0x426a36 });
  const stems = new THREE.InstancedMesh(stemGeometry, stemMaterial, 7);
  const grains = new THREE.InstancedMesh(grainGeometry, grainMaterial, 98);
  const leaves = new THREE.InstancedMesh(leafGeometry, leafMaterial, 14);
  let grainIndex = 0,
    leafIndex = 0;
  for (let i = 0; i < 7; i++) {
    const stalk = new THREE.Group();
    const stem = new THREE.Mesh(stemGeometry, stemMaterial);
    stalk.add(stem);
    for (let j = 0; j < 7; j++) {
      for (const side of [-1, 1]) {
        const grain = new THREE.Mesh(grainGeometry, grainMaterial);
        grain.scale.set(0.8, 1.9, 0.7);
        grain.position.set(side * (0.11 - j * 0.008), 1.05 + j * 0.16, 0);
        grain.rotation.z = side * -0.6;
        stalk.add(grain);
      }
    }
    for (let j = 0; j < 2; j++) {
      const leaf = new THREE.Mesh(leafGeometry, leafMaterial);
      leaf.scale.set(0.13, 0.65, 0.035);
      leaf.position.set(j ? 0.27 : -0.27, j ? 0.3 : -0.25, 0);
      leaf.rotation.z = j ? -0.6 : 0.6;
      stalk.add(leaf);
    }
    stalk.position.set(
      (i - 3) * 0.39 + 0.4,
      -0.3 + Math.sin(i * 2) * 0.2,
      Math.sin(i) * 0.3,
    );
    stalk.rotation.z = (3 - i) * 0.1;
    stalk.updateMatrixWorld(true);
    stalk.children.forEach((mesh) => {
      if (!(mesh instanceof THREE.Mesh)) return;
      if (mesh.geometry === stemGeometry)
        stems.setMatrixAt(i, mesh.matrixWorld);
      else if (mesh.geometry === grainGeometry)
        grains.setMatrixAt(grainIndex++, mesh.matrixWorld);
      else leaves.setMatrixAt(leafIndex++, mesh.matrixWorld);
    });
  }
  crop.add(stems, grains, leaves);
  crop.rotation.y = -0.25;
  scene.add(crop);
  const resize = new ResizeObserver(() => {
    const { width, height } = host.getBoundingClientRect();
    renderer.setSize(width, height, false);
    camera.aspect = width / Math.max(height, 1);
    camera.updateProjectionMatrix();
  });
  resize.observe(host);
  let visible = false,
    frame = 0,
    last = 0,
    disposed = false;
  const tick = (time: number) => {
    if (disposed || !visible || document.hidden) {
      frame = 0;
      return;
    }
    // Cap the decorative animation at 30fps and pause entirely outside the viewport.
    if (time - last >= 33) {
      crop.rotation.z = Math.sin(time * 0.0006) * 0.025;
      renderer.render(scene, camera);
      last = time;
    }
    frame = requestAnimationFrame(tick);
  };
  const resume = () => {
    if (!frame && visible && !document.hidden)
      frame = requestAnimationFrame(tick);
  };
  const intersection = new IntersectionObserver((entries) => {
    visible = entries[0].isIntersecting;
    resume();
  });
  intersection.observe(host);
  document.addEventListener("visibilitychange", resume);
  const contextLost = (event: Event) => {
    event.preventDefault();
    dispose();
  };
  renderer.domElement.addEventListener("webglcontextlost", contextLost);
  function dispose() {
    if (disposed) return;
    disposed = true;
    cancelAnimationFrame(frame);
    resize.disconnect();
    intersection.disconnect();
    document.removeEventListener("visibilitychange", resume);
    renderer.domElement.removeEventListener("webglcontextlost", contextLost);
    [
      stemGeometry,
      grainGeometry,
      leafGeometry,
      stemMaterial,
      grainMaterial,
      leafMaterial,
    ].forEach((resource) => resource.dispose());
    stems.dispose();
    grains.dispose();
    leaves.dispose();
    renderer.dispose();
    host.classList.remove("has-webgl");
    renderer.domElement.remove();
  }
  return dispose;
}
