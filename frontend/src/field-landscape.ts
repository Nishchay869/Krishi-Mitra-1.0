import * as THREE from 'three'

// A decorative field study, not live crop or sensor data.
export function createFieldLandscape(host: HTMLElement): () => void {
  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'low-power' })
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5))
  renderer.setClearColor(0x000000, 0)
  renderer.domElement.setAttribute('aria-hidden', 'true')
  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(36, 1, 0.1, 60)
  camera.position.set(7, 7, 9)
  camera.lookAt(0, 0, 0)
  const field = new THREE.Group()
  scene.add(field)
  scene.add(new THREE.HemisphereLight(0xf7ffd9, 0x243e24, 3))
  const sun = new THREE.DirectionalLight(0xe4ffad, 3)
  sun.position.set(3, 6, 4)
  scene.add(sun)
  const height = (x: number, z: number) => Math.sin(x * .7) * .3 + Math.cos(z * .65) * .3
  const ground = new THREE.PlaneGeometry(7, 7, 35, 35)
  ground.rotateX(-Math.PI / 2)
  const positions = ground.attributes.position
  for (let i = 0; i < positions.count; i++) positions.setY(i, height(positions.getX(i), positions.getZ(i)))
  ground.computeVertexNormals()
  const earth = new THREE.MeshStandardMaterial({ color: 0x274a2e, roughness: 1, side: THREE.DoubleSide })
  field.add(new THREE.Mesh(ground, earth))
  const gridGeometry = new THREE.WireframeGeometry(ground)
  const gridMaterial = new THREE.LineBasicMaterial({ color: 0xb5e879, transparent: true, opacity: .16 })
  field.add(new THREE.LineSegments(gridGeometry, gridMaterial))
  const plantGeometry = new THREE.ConeGeometry(.055, .28, 4)
  const plantMaterial = new THREE.MeshStandardMaterial({ color: 0xb4dc64, roughness: .8 })
  const plants = new THREE.InstancedMesh(plantGeometry, plantMaterial, 324)
  const dummy = new THREE.Object3D()
  for (let row = 0; row < 18; row++) for (let col = 0; col < 18; col++) {
    const x = (col - 8.5) * .34, z = (row - 8.5) * .34
    dummy.position.set(x, height(x, z) + .14, z)
    dummy.rotation.set(0, row * .2, Math.sin(col) * .1)
    dummy.updateMatrix()
    plants.setMatrixAt(row * 18 + col, dummy.matrix)
  }
  field.add(plants)
  const ringGeometry = new THREE.TorusGeometry(.36, .012, 5, 44)
  const ringMaterial = new THREE.MeshBasicMaterial({ color: 0xc8f53b, transparent: true, opacity: .9 })
  const rings: THREE.Mesh[] = []
  for (const [x, z] of [[-1.7, 1.4], [1.6, -.9], [.4, 2.1]]) {
    const ring = new THREE.Mesh(ringGeometry, ringMaterial)
    ring.rotation.x = -Math.PI / 2
    ring.position.set(x, height(x, z) + .35, z)
    field.add(ring)
    rings.push(ring)
  }
  host.appendChild(renderer.domElement)
  host.classList.add('field-ready')
  const size = () => {
    const { width, height: h } = host.getBoundingClientRect()
    renderer.setSize(Math.max(width, 1), Math.max(h, 1), false)
    camera.aspect = width / Math.max(h, 1)
    camera.updateProjectionMatrix()
  }
  const resize = new ResizeObserver(size)
  resize.observe(host)
  size()
  let target = 0, visible = false, frame = 0, last = 0, disposed = false
  const pointer = (event: PointerEvent) => {
    if (event.pointerType === 'touch') return
    const bounds = host.getBoundingClientRect()
    target = ((event.clientX - bounds.left) / bounds.width - .5) * .45
  }
  const reset = () => { target = 0 }
  host.addEventListener('pointermove', pointer)
  host.addEventListener('pointerleave', reset)
  const tick = (time: number) => {
    if (disposed || !visible || document.hidden) { frame = 0; return }
    if (time - last > 33) {
      field.rotation.y += (target - field.rotation.y) * .05
      field.position.y = Math.sin(time * .0005) * .06
      rings.forEach((ring, i) => ring.scale.setScalar(1 + Math.sin(time * .0016 + i * 2) * .12))
      renderer.render(scene, camera)
      last = time
    }
    frame = requestAnimationFrame(tick)
  }
  const resume = () => { if (!disposed && !frame && visible && !document.hidden) frame = requestAnimationFrame(tick) }
  const intersection = new IntersectionObserver(entries => { visible = entries[0].isIntersecting; resume() })
  intersection.observe(host)
  document.addEventListener('visibilitychange', resume)
  const lost = (event: Event) => { event.preventDefault(); dispose() }
  renderer.domElement.addEventListener('webglcontextlost', lost)
  function dispose() {
    if (disposed) return
    disposed = true
    cancelAnimationFrame(frame)
    resize.disconnect()
    intersection.disconnect()
    document.removeEventListener('visibilitychange', resume)
    host.removeEventListener('pointermove', pointer)
    host.removeEventListener('pointerleave', reset)
    renderer.domElement.removeEventListener('webglcontextlost', lost)
    ;[ground, earth, gridGeometry, gridMaterial, plantGeometry, plantMaterial, ringGeometry, ringMaterial].forEach(resource => resource.dispose())
    plants.dispose()
    renderer.dispose()
    renderer.domElement.remove()
    host.classList.remove('field-ready')
  }
  return dispose
}
