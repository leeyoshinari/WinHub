const container = document.getElementById('canvas-box'); // 容器
const sound_btn = document.getElementById('sound_btn'); // 按钮音效
const sound_back = document.getElementById('sound_back'); // 背景音乐
const dom_success = document.getElementById("success"); // 成功界面
const dom_music_btn = document.getElementById("music-btn"); // 音乐开关按钮
const boss = document.getElementById('boss');
const setting = checkSetting();
let world; // 物理世界对象
let scene; // 场景
let camera; // 相机
let renderer; // 渲染器
let animateId; // 用于停止动画循环
let cic = []; // 小圈圈
let body_cic = []; // 小圈圈刚体
let ground = []; // 四周的墙壁
let pins = []; // 两根柱子
let boxW,boxH; // 容器真实宽高，px
let threeW, threeH; // three中的盒子宽高

window.onload = function(){
  FastClick.attach(document.body);
  if(setting === 'pc'){
    document.querySelectorAll('.yu').forEach((item)=>{
      item.style.animationDuration = '8s';
      item.style.webkitAnimationDuration = '8s';
    })
    // boss.style.width = '640px';
  }
  document.querySelectorAll('.i18n').forEach(ele => {ele.innerText = window.parent.i18next.t(ele.getAttribute('key'));})
  window.parent.document.querySelectorAll('.window.game>.titbar>span>.title')[0].innerText = window.parent.i18next.t('game.rings');
  boss.classList.add('show');
  boxW = container.offsetWidth;
  boxH = container.offsetHeight;
  threeH = 100;
  threeW = (boxW / boxH) * threeH;

  document.getElementById("btn_left").addEventListener('click', ()=> onBtnClick('left'),false);
  document.getElementById("btn_right").addEventListener('click', ()=> onBtnClick('right'),false);
  document.getElementById("reset-btn").addEventListener("click", onResetClick, false);
  document.getElementById("new-game").addEventListener("click", onNewGame, false);
  document.getElementById("music-btn").addEventListener("click", onMusicClick, false);

  init3boss();
  initWorld();
  initLights();
  initDecoration();

  initGround();
  initPins();
  initCircle();
  initRay();

  initPaoPao();
  window.addEventListener('resize', resize, false);
  animate();
}

/** 判断是手机还是PC **/
function checkSetting(){
  if((navigator.userAgent.match(/(phone|pad|pod|iPhone|iPod|ios|iPad|Android|Mobile|BlackBerry|IEMobile|MQQBrowser|JUC|Fennec|wOSBrowser|BrowserNG|WebOS|Symbian|Windows Phone)/i))) {
    return 'phone';
  } else {
    return 'pc';
  }
}

/** 初始化三要素 **/
function init3boss() {
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(90, boxW / boxH, 0.1, 200);
  renderer = new THREE.WebGLRenderer({alpha: true, antialias: true});

  camera.position.set(0, 0, 50);
  camera.lookAt(new THREE.Vector3(0, 0, 0));

  // 100前景ground高度，50-相机到ground的距离，不用算了，距离和高度固定，结果等于90度
  // 不过过程还是写在这
  // camera.fov = Math.atan((100/2)/50) * 2 * (180 / Math.PI);
  // camera.updateProjectionMatrix();

  renderer.setSize(boxW, boxH, true);
  renderer.gammaOutput = true; // 所有纹理和颜色需要乘以gamma输出，颜色会亮丽许多
  renderer.setClearColor(0x000000,0);
  container.appendChild(renderer.domElement);
}

/** 窗体大小改变时重置分辨率等参数 **/
function resize() {
  boxW = container.offsetWidth;
  boxH = container.offsetHeight;
  camera.aspect = boxW / boxH;
  camera.updateProjectionMatrix();
  renderer.setSize(boxW, boxH);
}

/** 动画循环 **/
function animate() {
  animateId = requestAnimationFrame(animate);
  render();
}

/** 渲染内容 **/
let timeOld = Date.now();
let timeNow = timeOld;
function render() {
  if (world == null) return;

  world.step(); // 更新world
  for(let i=0;i < body_cic.length;i++){
    cic[i].position.copy(body_cic[i].getPosition());
    cic[i].quaternion.copy(body_cic[i].getQuaternion());
  }

  timeNow = Date.now();
  if(timeNow - timeOld > 5000){
    checkLock();
    timeOld = timeNow;
  }
  renderer.render(scene, camera);
}

/** 创建world **/
function initWorld() {
  world = new OIMO.World({
    timestep: 1 / 60, // 刷新频率
    iterations: 8, // 迭代次数
    broadphase: 2, // 物理类型？1蛮力计算，2扫描和修剪，3卷积树
    info: false, // 是否输出统计信息
    worldscale: 1, // 世界缩放比例
    random: true, // 随机因子
    gravity: [0, -9.8, 0], // 重力加速度矢量
  });
}

/** 创建ground **/
/** 墙体原料 **/
const ground_material = new THREE.MeshBasicMaterial({ color: 0x002200, transparent: true, opacity: 0 });
const ground_material1 = new THREE.MeshBasicMaterial({ color: 0x000022, transparent: true, opacity: 0.05 });
let ground_geometry; // 地面geometry

function initGround() {
  ground_geometry = new THREE.BoxBufferGeometry(threeW, threeH, 1); // 地面geometry
  ground.push(new THREE.Mesh(ground_geometry, ground_material)); // 正面
  ground[0].position.set(0, 0, 0.1);

  ground.push(new THREE.Mesh(ground_geometry, ground_material1)); // 背面
  ground[1].position.set(0, 0, -10); // 正面与背面距离10

  ground.push(new THREE.Mesh(ground_geometry, ground_material1)); // 左边
  ground[2].rotation.set(0, Math.PI / 2, 0);
  ground[2].position.set(-threeW/2, 0, 0);

  ground.push(ground[2].clone()); // 右边
  ground[3].position.set(threeW/2, 0, 0);

  ground.push(new THREE.Mesh(ground_geometry, ground_material1)); // 上边
  ground[4].rotation.set(Math.PI / 2, 0, 0);
  ground[4].position.set(0, threeH/2, 0);

  ground.push(ground[4].clone()); // 下边
  ground[5].position.set(0, -threeH/2, 0);
  
  ground.forEach((item)=>{
    scene.add(item);
  })

  world.add({ size: [threeW, threeH, 2], pos: [0, 0, 0.1],friction: 0, world }); // 正面
  world.add({ size: [threeW, threeH, 2], pos: [0, 0, -10], friction: 0,world }); // 背面
  world.add({ size: [threeW, threeH, 2], pos: [-threeW/2, 0, 0], rot: [0, 90, 0],friction: 0, world }); // 左边
  world.add({ size: [threeW, threeH, 2], pos: [threeW/2, 0, 0], rot: [0, 90, 0], friction: 0,world }); // 右边
  world.add({ size: [threeW, threeH, 2], pos: [0, threeH/2, 0], rot: [90, 0, 0], friction: 0,world }); // 上边
  world.add({ size: [threeW, threeH, 2], pos: [0, -threeH/2, 0], rot: [90, 0, 0], friction: 0,world }); // 下边
}

/** 创建一些装饰物 **/
function initDecoration(){
  new THREE.TextureLoader().load( './assets/imgs/hole.png', function(texture){
    const geometry = new THREE.CircleBufferGeometry(2, 12);
    const material = new THREE.MeshBasicMaterial({color: 0xffffff,map:texture,transparent:true});

    const mesh = new THREE.Mesh(geometry, material);
    const mesh2 = mesh.clone();

    mesh.position.set(-threeW/2 + 10,1-threeH/2, -4);  
    mesh2.position.set(threeW/2 - 10, 1-threeH/2, -4);

    scene.add(mesh);
    scene.add(mesh2);
  });
}

/** 光 */
function initLights(){
  scene.add(new THREE.AmbientLight(0x222222));
  const l2 = new THREE.DirectionalLight(0xcccccc, 1);
  l2.position.set(0,5,10);
  scene.add(l2);
}

/**================
 * 私有 - 初始化柱子的射线
 * =============**/
 let rayLeft;
 let rayRight;
 function initRay() {
   const leftP = pins[2].position;
   const rightP = pins[5].position;
 
   rayLeft = new THREE.Raycaster(new THREE.Vector3(leftP.x, leftP.y - 12, leftP.z), new THREE.Vector3(0, 1, 0), 0, 22);
   rayLeft.intersectObjects(cic_in);
   rayRight = new THREE.Raycaster(new THREE.Vector3(rightP.x, rightP.y - 12, rightP.z), new THREE.Vector3(0, 1, 0), 0, 22);
   rayRight.intersectObjects(cic_in);

    // const arrowHelper = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(rightP.x, rightP.y - 12, rightP.z), 23, 0xffffff, 5, 5);
    // scene.add(arrowHelper);
 }

/** 判断所有小圈套住的情况 **/
/**
 * 小圆圈半径4，圆心到内表面距离3.4，小环本身半径0.6
 * 中间pin半径1
 */
// 左边判定条件
let lockNum = 0;

function checkLock(){
  const intersectsL = rayLeft.intersectObjects(cic_in);
  const intersectsR = rayRight.intersectObjects(cic_in);

  const locksArr = [...intersectsL, ...intersectsR];
  lockNum = locksArr.length;

  for (let i = 0; i < body_cic.length; i++) {
    cic[i].isLock = false;
  }
  for (let i = 0; i < locksArr.length; i++) {
    cic[locksArr[i].object.parentIndex].isLock = true;
  }
  // todo check
  if (lockNum >= 10) {
    gameSuccess();
  }
}

/** 初始化所有的pin **/
/** pin原料 **/
const size = [2, 2, 5, 3.6, 12, 12, 1, 24, 1];
const pin_box = new THREE.BoxBufferGeometry(size[0], size[1], size[2]);
const pin_box2 = new THREE.SphereBufferGeometry(size[3], size[4], size[5]);
const pin_box3 = new THREE.CylinderBufferGeometry(0.4, 1.4, 24, 24, 24);
const pin_material = new THREE.MeshPhongMaterial({ color: 0xaaaaff });

function initPins() {
  const pos = [
    -threeW / 2 / 2, -20, -7.5,
    -threeW / 2 / 2, -20, -4,
    -threeW / 2 / 2, -8, -4
  ];

  pins.push(new THREE.Mesh(pin_box, pin_material));
  pins.push(new THREE.Mesh(pin_box2, pin_material));
  pins.push(new THREE.Mesh(pin_box3, pin_material));

  scene.add(pins[0]);
  scene.add(pins[1]);
  scene.add(pins[2]);

  const body1 = world.add({
    type: 'box',
    size: [size[0], size[1], size[2]],
    pos: [pos[0], pos[1], pos[2]],
    world: world,
  });
  const body2 = world.add({
    type: 'box',
    size: [size[3]],
    pos: [pos[3], pos[4], pos[5]],
    world: world,
  });
  const body3 = world.add({
    type: 'box',
    size: [size[6], size[7], size[8]],
    pos: [pos[6], pos[7], pos[8]],
    world: world,
  });
  pins[0].position.copy(body1.getPosition());
  pins[1].position.copy(body2.getPosition());
  pins[2].position.copy(body3.getPosition());

  scene.add(pins[0]);
  scene.add(pins[1]);
  scene.add(pins[2]);

  // 创建右边的
  pins.push(pins[0].clone());
  pins.push(pins[1].clone());
  pins.push(pins[2].clone());

  const rbody1 = world.add({
    type: 'box',
    size: [size[0], size[1], size[2]],
    pos: [-pos[0], pos[1], pos[2]],
    world: world,
  });
  const rbody2 = world.add({
    type: 'box',
    size: [size[3]],
    pos: [-pos[3], pos[4], pos[5]],
    world: world,
  });
  const rbody3 = world.add({
    type: 'box',
    size: [size[6], size[7], size[8]],
    pos: [-pos[6], pos[7], pos[8]],
    world: world,
  });

  pins[3].position.copy(rbody1.getPosition());
  pins[4].position.copy(rbody2.getPosition());
  pins[5].position.copy(rbody3.getPosition());

  scene.add(pins[3]);
  scene.add(pins[4]);
  scene.add(pins[5]);
}

/** 初始化10个小圆圈 **/
const cic_geometry = new THREE.TorusBufferGeometry( 4, 0.6, 8, 32 );
const cic_material = [
  new THREE.MeshToonMaterial( { color: 0xdd0000 } ),
  new THREE.MeshToonMaterial( { color: 0x2244dd } ),
  new THREE.MeshToonMaterial( { color: 0xdddd00 } ),
  new THREE.MeshToonMaterial( { color: 0x00dd00 } )
];
const cic_geo_in = new THREE.CircleGeometry(3.4, 16);
const cic_material_in = new THREE.MeshToonMaterial({ color: 0x000000, side: THREE.DoubleSide, transparent: true, opacity: 0 });
const cic_in = []; // 需要检测相交性的对象

function initCircle(){
  const types = ['box','box','box','box','box','box','box','box','box','box','box','box'];
  const sizes = [
    1,2.2,1,
    1,2.2,1,
    1,2.2,1,
    1,2.2,1,
    1,2.2,1,
    1,2.2,1,
    1,2.2,1,
    1,2.2,1,
    1,2.2,1,
    1,2.2,1,
    1,2.2,1,
    1,2.2,1,
  ];
  
  const ros = [
    30,30,0,
    60,60, -30,
    90,90,-60,
    120,30,-90,
    150,60,60,
    180,90,30,
    210,30,0,
    240,60, -30 ,
    270,90,-60,
    300,30, 90,
    330,60,60,
    360,90,30,
  ];

  const l = 3.5; // 圆心到顶点距离
  const r_d = (Math.cos(Math.PI/180 * 15) * l); // 圆心到边距离

  const pos = [
    -r_d,0,0,
    -Math.cos(Math.PI/180 * 30) * r_d, Math.sin(Math.PI/180 * 30) * r_d,0,
    -Math.cos(Math.PI/180 * 60) * r_d, Math.sin(Math.PI/180 * 60) * r_d,0,
    0,r_d,0,
    Math.cos(Math.PI/180 * 60) * r_d, Math.sin(Math.PI/180 * 60) * r_d, 0,
    Math.cos(Math.PI/180 * 30) * r_d, Math.sin(Math.PI/180 * 30) * r_d,0,
    r_d,0,0,
    Math.cos(Math.PI/180 * 30) * r_d, -Math.sin(Math.PI/180 * 30) * r_d,0,
    Math.cos(Math.PI/180 * 60) * r_d, -Math.sin(Math.PI/180 * 60) * r_d, 0,
    0,-r_d,0,
    -Math.cos(Math.PI/180 * 60) * r_d, -Math.sin(Math.PI/180 * 60) * r_d,0,
    -Math.cos(Math.PI/180 * 30) * r_d, -Math.sin(Math.PI/180 * 30) * r_d,0,
  ];

  for(let i=0;i<10;i++){
    let x,y;
    if(i<5){
      x = -20 + i*10;
      y = 40;
    } else {
      x = -70 +i*10;
      y = 30;
    }
    const wc = world.add({
      type: types,
      size: sizes,
      posShape: pos,
      pos: [x,y,-5],
      rot: ros,
      friction: 0.4,
      move:true ,

      name: `cic${i}`
    });

    const c = new THREE.Mesh( cic_geometry, cic_material[random(0,3)] );
    const c_in = new THREE.Mesh(cic_geo_in, cic_material_in);
    c_in.parentIndex = i;
    c.add(c_in);

    cic.push(c);
    body_cic.push(wc);
    cic_in.push(c_in);
    scene.add(c);
  }
}

/** 取范围随机数 **/
function random(min,max){
  return Math.round(Math.random() * (max-min) + min);
}

/** 按钮被点击 **/
function onBtnClick(t){
  if(music){
    sound_btn.currentTime = 0;
    sound_btn.play();
  }
  const z = Math.random() * 20 - 10;
  for(let i=0;i<body_cic.length;i++){
    const p = cic[i].position;
    const lock = cic[i].isLock ? 4 : 1;
    
    if(t === 'left'){
      const s_x = Math.abs(p.x - (- threeW/2));
      const s_y = Math.abs(p.y - (- threeH/2));
      const far = Math.sqrt(s_x**2 + s_y**2);
      body_cic[i].applyImpulse(p, {x: (230 - far*2)/lock,y: (450 - far*2)/lock,z});
    } else {
      const s_x = Math.abs(p.x - ( threeW/2));
      const s_y = Math.abs(p.y - ( threeH/2));
      const far = Math.sqrt(s_x**2 + s_y**2);
      body_cic[i].applyImpulse(p, {x: (-230 + far*2)/lock,y: (450 - far*2)/lock,z});
    }
  }
  
}

/** 点击重新开始按钮 **/
function onResetClick(){  
  cancelAnimationFrame(animateId);
  world.clear();
  
  cic.forEach((item)=>{
    scene.remove(item);
  })
  
  ground.forEach((item)=>{
    scene.remove(item);
  });

  pins.forEach((item)=>{
    scene.remove(item);
  });

  body_cic.length = 0;
  cic_in.length = 0;
  ground.length = 0;
  cic.length = 0;
  pins.length = 0;

  initGround();
  initPins();
  initCircle();
  animate();
}

/** 随机刷泡泡 **/
const pao = document.querySelectorAll(".back-box .pao");
const yu = document.querySelectorAll(".back-box .yu");
pao.forEach((item)=>{
  item.addEventListener("animationend", onPaoAnimationend, false)
})
yu.forEach((item)=>{
  item.addEventListener("animationend", onYuAnimationend, false)
})
function initPaoPao(){
  setInterval(()=>{
    const p = pao[random(0,pao.length-1)];
    const y = yu[random(0,yu.length - 1)];
    if(p.getAttribute('isTrans')!=='t'){
      p.style.left = `${random(10, boxW-10)}px`;
      p.setAttribute('isTrans', 't');
      p.classList.add('pao-move');
    }
    if(y.getAttribute('isTrans')!=='t'){
      let type = Math.random() > 0.5;
      y.style.top = `${random(0, boxH/2)}px`;
      if(type){
        y.style.left = '-10vw';
        y.setAttribute('isTrans', 't');
        y.classList.add('yu-movetoright');
      } else {
        y.style.left = `100vw`;
        y.setAttribute('isTrans', 't');
        y.classList.add('yu-movetoleft');
      }
    }
  },2000)
}

function onPaoAnimationend(e){
  e.target.setAttribute('isTrans', 'f');
  e.target.classList.remove('pao-move');
}
function onYuAnimationend(e){
  e.target.setAttribute('isTrans', 'f');
  e.target.classList.remove('yu-movetoleft','yu-movetoright');
}
/** 游戏成功 **/
function gameSuccess(){
  cancelAnimationFrame(animateId);
  dom_success.classList.add("show");
  isLove = true;
  sound_back.pause();
  document.getElementById("sound_success").play();
  playLove();
}

/** 随机刷爱心 **/
const love = document.getElementById("love");
let isLove = false;
love.addEventListener("animationend", onLoveAnimationend, false);
function playLove(){
  love.style.left = `${random(10, boxW-10)}px`;
  love.style.top = `${random(50, boxH)}px`;
  love.classList.add('love-move');
}
function onLoveAnimationend(e){
  e.target.classList.remove('love-move');
  if(isLove){
    setTimeout(()=>playLove());
  }
}

/** 开始新的游戏 **/
function onNewGame(){
  isLove = false;
  if(music){
    sound_back.play();
  }
  onResetClick();
  dom_success.classList.remove("show");
}

/** 音乐开关 **/
let music = false;
function onMusicClick(){
  music = !music;

  if(music){
    dom_music_btn.classList.add("play");
    dom_music_btn.innerText = window.parent.i18next.t('game.ring.playing.music');
    sound_back.play();
  } else {
    dom_music_btn.classList.remove("play");
    dom_music_btn.innerText = window.parent.i18next.t('game.ring.open.music');
    sound_back.pause();
  }
}