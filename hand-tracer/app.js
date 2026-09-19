/**
 * CyberSuite PRO - AI Virtual Mouse & Rock-Paper-Scissors Instant Counter Arena
 * High-Performance Engine with MediaPipe Hands (Model Complexity 0 Lite)
 */

// ============================================================================
// 1. One-Euro Adaptive Filter (Ultra-Light Standard for Zero-Lag Precision)
// ============================================================================
class OneEuroFilter {
  constructor(minCutoff = 2.5, beta = 0.035, dCutoff = 1.0) {
    this.minCutoff = minCutoff;
    this.beta = beta;
    this.dCutoff = dCutoff;
    this.xPrev = null;
    this.dxPrev = 0;
    this.tPrev = null;
  }

  setParams(minCutoff, beta) {
    this.minCutoff = minCutoff;
    this.beta = beta;
  }

  alpha(cutoff, dt) {
    const tau = 1.0 / (2 * Math.PI * cutoff);
    return 1.0 / (1.0 + tau / dt);
  }

  filter(x, timestamp) {
    if (this.xPrev === null) {
      this.xPrev = x;
      this.dxPrev = 0;
      this.tPrev = timestamp;
      return x;
    }

    const dt = Math.max((timestamp - this.tPrev) / 1000.0, 0.001);
    this.tPrev = timestamp;

    const dx = (x - this.xPrev) / dt;
    const aD = this.alpha(this.dCutoff, dt);
    const edx = this.dxPrev + aD * (dx - this.dxPrev);
    this.dxPrev = edx;

    const cutoff = this.minCutoff + this.beta * Math.abs(edx);
    const a = this.alpha(cutoff, dt);
    const filteredX = this.xPrev + a * (x - this.xPrev);
    this.xPrev = filteredX;
    return filteredX;
  }

  reset() {
    this.xPrev = null;
    this.dxPrev = 0;
    this.tPrev = null;
  }
}

class Landmark3DFilter {
  constructor(minCutoff, beta) {
    this.fx = new OneEuroFilter(minCutoff, beta);
    this.fy = new OneEuroFilter(minCutoff, beta);
    this.fz = new OneEuroFilter(minCutoff, beta);
  }

  setParams(minCutoff, beta) {
    this.fx.setParams(minCutoff, beta);
    this.fy.setParams(minCutoff, beta);
    this.fz.setParams(minCutoff, beta);
  }

  filter(pt, time, outPt) {
    outPt.x = this.fx.filter(pt.x, time);
    outPt.y = this.fy.filter(pt.y, time);
    outPt.z = this.fz.filter(pt.z || 0, time);
    return outPt;
  }

  reset() {
    this.fx.reset();
    this.fy.reset();
    this.fz.reset();
  }
}

// 21 Landmark Filters (Standard Default: Ultra-Light, minCutoff: 2.5, beta: 0.035)
const handFilters = Array.from({ length: 21 }, () => new Landmark3DFilter(2.5, 0.035));

// Pre-allocated landmark buffers (ZERO garbage collection pauses!)
const filteredNormPoints = Array.from({ length: 21 }, () => ({ x: 0, y: 0, z: 0 }));
const smoothedPoints = Array.from({ length: 21 }, () => ({ x: 0, y: 0, z: 0 }));

// ============================================================================
// 2. Audio Synthesizer (Clicks, Chimes, RPS Sounds)
// ============================================================================
class TacticalAudio {
  constructor() {
    this.ctx = null;
    this.enabled = true;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) this.ctx = new AudioCtx();
    }
  }

  playClick() {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(1450, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(320, this.ctx.currentTime + 0.025);
      gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.025);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.025);
    } catch (e) {}
  }

  playToggle(active) {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    try {
      const freq = active ? 880 : 380;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
      gain.gain.setValueAtTime(0.06, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.06);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.06);
    } catch (e) {}
  }

  playMoveChange() {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(580, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(1200, this.ctx.currentTime + 0.05);
      gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.05);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.05);
    } catch (e) {}
  }

  playCountdownBeep(num) {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    try {
      const freq = num === 0 ? 1174 : 587; // D6 on shoot, D5 on 3/2/1
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
      gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + (num === 0 ? 0.2 : 0.08));
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + (num === 0 ? 0.2 : 0.08));
    } catch (e) {}
  }

  playVictoryFanfare() {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    const notes = [523.25, 659.25, 783.99, 1046.50]; // C Major
    notes.forEach((freq, idx) => {
      setTimeout(() => {
        try {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
          gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.18);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start();
          osc.stop(this.ctx.currentTime + 0.18);
        } catch (e) {}
      }, idx * 60);
    });
  }

  playDefeatTone() {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(320, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(140, this.ctx.currentTime + 0.22);
      gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.22);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.22);
    } catch (e) {}
  }
}

const sound = new TacticalAudio();

// ============================================================================
// 3. Configuration & State
// ============================================================================
const CONFIG = {
  smoothingPresets: {
    1: { name: 'Ultra-Light (Standard)', minCutoff: 2.5, beta: 0.035, cutoffText: '2.5 Hz', betaText: '0.035', lagText: '< 2ms' },
    2: { name: 'Light', minCutoff: 1.5, beta: 0.020, cutoffText: '1.5 Hz', betaText: '0.020', lagText: '~4ms' },
    3: { name: 'Balanced', minCutoff: 0.8, beta: 0.010, cutoffText: '0.8 Hz', betaText: '0.010', lagText: '~8ms' },
    4: { name: 'Steady', minCutoff: 0.35, beta: 0.005, cutoffText: '0.35 Hz', betaText: '0.005', lagText: '~14ms' }
  },
  skeletonConnections: [
    [0, 1], [1, 2], [2, 3], [3, 4],
    [0, 5], [5, 6], [6, 7], [7, 8],
    [0, 9], [9, 10], [10, 11], [11, 12],
    [0, 13], [13, 14], [14, 15], [15, 16],
    [0, 17], [17, 18], [18, 19], [19, 20],
    [5, 9], [9, 13], [13, 17], [0, 5], [0, 17]
  ]
};

const COUNTER_MAP = {
  rock: 'paper',
  paper: 'scissors',
  scissors: 'rock'
};

const RPS_ICONS = {
  rock: '✊',
  paper: '✋',
  scissors: '✌️',
  waiting: '❓',
  none: '🤖'
};

const TAUNTS = [
  "I read your intent before your muscles fired.",
  "Paper wraps Rock effortlessly.",
  "Scissors slice clean through Paper.",
  "Rock pulverizes Scissors into dust.",
  "Calculated your move in milliseconds.",
  "Human reflex: ~250ms. Cyber AI: 8ms.",
  "Predictable neural pattern!",
  "Nice try, human!"
];

const state = {
  // App Mode: 'mouse' | 'rps'
  appMode: 'mouse',

  // Master Virtual Mouse State
  active: true,
  isMiniMode: false,
  trackingMode: 'relative',
  screenWidth: 1920,
  screenHeight: 1080,
  cursorX: 960,
  cursorY: 540,
  lastSentX: -1,
  lastSentY: -1,

  isPointingEngaged: false,
  lastTrackedIndexPos: null,

  smoothingLevel: 1,
  sensitivity: 1.6,
  thumbTapThreshold: 0.32,
  reach: 60,

  gestureState: 'searching',
  isThumbTapping: false,
  isScrolling: false,
  lastScrollY: null,

  // Rock-Paper-Scissors Battle State
  rpsMode: 'instant', // 'instant' (Mind-Reader) | 'tournament' (3-2-1)
  rpsPlayerMove: 'none',
  rpsAiMove: 'none',
  rpsPoseStartTime: performance.now(),
  rpsScores: { player: 0, ai: 0, draws: 0 },
  rpsStreak: 0,
  rpsTournamentState: 'idle', // 'idle' | 'counting' | 'result'
  rpsCountdownVal: 3,
  rpsCountdownTimer: null,

  // Display & Feedback
  showSkeleton: true,
  showScreenBox: true,
  mirror: true,
  sound: true,

  clickRipples: [],
  fps: 0,
  frameCount: 0,
  lastFpsUpdate: performance.now(),
  lastUiUpdate: 0
};

// ============================================================================
// 4. DOM Elements
// ============================================================================
const appContainer = document.getElementById('appContainer');
const videoElement = document.getElementById('webcam');
const outputCanvas = document.getElementById('outputCanvas');
const outCtx = outputCanvas.getContext('2d', { alpha: false });
const loadingOverlay = document.getElementById('loadingOverlay');

// Navigation Tabs
const tabBtnMouse = document.getElementById('tabBtnMouse');
const tabBtnRPS = document.getElementById('tabBtnRPS');
const mouseSettingsDeck = document.getElementById('mouseSettingsDeck');
const rpsSettingsDeck = document.getElementById('rpsSettingsDeck');
const rpsArenaOverlay = document.getElementById('rpsArenaOverlay');
const brandSubtitle = document.getElementById('brandSubtitle');
const footerModeText = document.getElementById('footerModeText');

// Badges & Mouse Controls
const masterToggleBtn = document.getElementById('masterToggleBtn');
const masterToggleText = document.getElementById('masterToggleText');
const masterToggleSwitch = document.getElementById('masterToggleSwitch');
const gestureDot = document.getElementById('gestureDot');
const gestureValue = document.getElementById('gestureValue');
const coordValue = document.getElementById('coordValue');
const fpsValue = document.getElementById('fpsValue');
const trackingIndicatorText = document.getElementById('trackingIndicatorText');
const miniStatusText = document.getElementById('miniStatusText');
const miniDot = document.getElementById('miniDot');
const screenBoxLabel = document.getElementById('screenBoxLabel');
const gestureHintsBar = document.getElementById('gestureHintsBar');

const modeRelativeBtn = document.getElementById('modeRelative');
const modeAbsoluteBtn = document.getElementById('modeAbsolute');
const reachRow = document.getElementById('reachRow');
const reachInput = document.getElementById('reachInput');
const reachVal = document.getElementById('reachVal');

const smoothingLevelInput = document.getElementById('smoothingLevel');
const smoothingVal = document.getElementById('smoothingVal');
const filterMetrics = document.getElementById('filterMetrics');
const sensitivityInput = document.getElementById('sensitivityInput');
const sensitivityVal = document.getElementById('sensitivityVal');
const thumbTapInput = document.getElementById('thumbTapInput');
const thumbTapVal = document.getElementById('thumbTapVal');

const toggleSkeleton = document.getElementById('toggleSkeleton');
const toggleScreenBox = document.getElementById('toggleScreenBox');
const toggleMirror = document.getElementById('toggleMirror');
const toggleSound = document.getElementById('toggleSound');
const toggleMiniBtn = document.getElementById('toggleMiniBtn');
const miniRestoreBtn = document.getElementById('miniRestoreBtn');
const miniHudActionBtn = document.getElementById('miniHudActionBtn');
const testClickBtn = document.getElementById('testClickBtn');

// RPS Battle Elements
const rpsPlayerCard = document.getElementById('rpsPlayerCard');
const rpsPlayerIcon = document.getElementById('rpsPlayerIcon');
const rpsPlayerMoveText = document.getElementById('rpsPlayerMoveText');
const rpsAiCard = document.getElementById('rpsAiCard');
const rpsAiIcon = document.getElementById('rpsAiIcon');
const rpsAiMoveText = document.getElementById('rpsAiMoveText');
const rpsAiTaunt = document.getElementById('rpsAiTaunt');
const rpsVsEmblem = document.getElementById('rpsVsEmblem');
const rpsCountdownOrb = document.getElementById('rpsCountdownOrb');
const rpsResultToast = document.getElementById('rpsResultToast');
const rpsReactionVal = document.getElementById('rpsReactionVal');
const rpsModeInstant = document.getElementById('rpsModeInstant');
const rpsModeTournament = document.getElementById('rpsModeTournament');
const rpsTournamentControls = document.getElementById('rpsTournamentControls');
const rpsStartRoundBtn = document.getElementById('rpsStartRoundBtn');
const rpsResetScoreBtn = document.getElementById('rpsResetScoreBtn');
const rpsScorePlayer = document.getElementById('rpsScorePlayer');
const rpsScoreAi = document.getElementById('rpsScoreAi');
const rpsScoreDraw = document.getElementById('rpsScoreDraw');
const rpsStreakBadge = document.getElementById('rpsStreakBadge');
const rpsLatencyMetric = document.getElementById('rpsLatencyMetric');

// ============================================================================
// 5. Geometry & Coordinate Helpers
// ============================================================================
function resizeCanvas() {
  const container = document.getElementById('canvasContainer');
  if (!container) return;
  const width = container.clientWidth;
  const height = container.clientHeight;

  if (width > 50 && height > 50) {
    if (outputCanvas.width !== width || outputCanvas.height !== height) {
      outputCanvas.width = width;
      outputCanvas.height = height;
    }
  }
}
window.addEventListener('resize', resizeCanvas);

function distFast(p1, p2) {
  const dx = p1.x - p2.x;
  const dy = p1.y - p2.y;
  return Math.sqrt(dx * dx + dy * dy);
}

// ============================================================================
// 6. Gesture Classifiers
// ============================================================================

// Virtual Mouse Gesture Classifier
function classifyMouseGestures(rawLandmarks, points) {
  const wrist = rawLandmarks[0];
  const thumbTip = rawLandmarks[4];
  const indexTip = rawLandmarks[8];
  const indexPip = rawLandmarks[6];

  const middleTip = rawLandmarks[12];
  const middlePip = rawLandmarks[10];
  const middleMcp = rawLandmarks[9];

  const ringTip = rawLandmarks[16];
  const ringPip = rawLandmarks[14];

  const pinkyTip = rawLandmarks[20];
  const pinkyPip = rawLandmarks[18];

  const isIndexExtended = distFast(wrist, indexTip) > distFast(wrist, indexPip) * 1.18;
  const isMiddleExtended = distFast(wrist, middleTip) > distFast(wrist, middlePip) * 1.15;
  const isRingExtended = distFast(wrist, ringTip) > distFast(wrist, ringPip) * 1.15;
  const isPinkyExtended = distFast(wrist, pinkyTip) > distFast(wrist, pinkyPip) * 1.15;

  let otherCurledCount = 0;
  if (!isMiddleExtended) otherCurledCount++;
  if (!isRingExtended) otherCurledCount++;
  if (!isPinkyExtended) otherCurledCount++;

  const extendedCount = (isIndexExtended ? 1 : 0) + (isMiddleExtended ? 1 : 0) + (isRingExtended ? 1 : 0) + (isPinkyExtended ? 1 : 0);
  if (extendedCount >= 4) {
    return { type: 'clutch', label: '✋ Open Palm (Clutched • Reposition)' };
  }

  if (extendedCount === 0) {
    return { type: 'standby', label: '✊ Fist (Paused)' };
  }

  if (isIndexExtended && isMiddleExtended && !isRingExtended && !isPinkyExtended) {
    return { type: 'scrolling', label: '✌️ Two-Finger Scroll' };
  }

  if (isIndexExtended && otherCurledCount >= 2) {
    const handScale = distFast(wrist, middleMcp) || 0.2;

    const dThumbMiddlePip = distFast(thumbTip, middlePip) / handScale;
    const dThumbMiddleMcp = distFast(thumbTip, middleMcp) / handScale;
    const dThumbIndexPip = distFast(thumbTip, indexPip) / handScale;
    const dThumbIndexTip = distFast(thumbTip, indexTip) / handScale;

    const contactMetric = Math.min(dThumbMiddlePip, dThumbMiddleMcp, dThumbIndexPip, dThumbIndexTip);

    const tapOnThreshold = state.thumbTapThreshold;
    const tapOffThreshold = state.thumbTapThreshold * 1.35;

    let isTapping = state.isThumbTapping;
    if (!state.isThumbTapping && contactMetric < tapOnThreshold) {
      isTapping = true;
    } else if (state.isThumbTapping && contactMetric > tapOffThreshold) {
      isTapping = false;
    }

    return {
      type: isTapping ? 'thumb_tap' : 'pointing',
      label: isTapping ? '💥 Thumb Tap (Single Click)' : '👉 Pointing (Active)',
      isThumbTapping: isTapping,
      contactMetric,
      thumbPoint: points[4],
      indexPoint: points[8]
    };
  }

  return { type: 'standby', label: '✋ Standby' };
}

// Rock Paper Scissors Gesture Classifier
function classifyRPS(rawLandmarks) {
  const wrist = rawLandmarks[0];
  const indexTip = rawLandmarks[8];
  const indexPip = rawLandmarks[6];
  const middleTip = rawLandmarks[12];
  const middlePip = rawLandmarks[10];
  const ringTip = rawLandmarks[16];
  const ringPip = rawLandmarks[14];
  const pinkyTip = rawLandmarks[20];
  const pinkyPip = rawLandmarks[18];

  const isIndex = distFast(wrist, indexTip) > distFast(wrist, indexPip) * 1.16;
  const isMiddle = distFast(wrist, middleTip) > distFast(wrist, middlePip) * 1.14;
  const isRing = distFast(wrist, ringTip) > distFast(wrist, ringPip) * 1.14;
  const isPinky = distFast(wrist, pinkyTip) > distFast(wrist, pinkyPip) * 1.14;

  // Rock: all 4 fingers curled into a fist
  if (!isIndex && !isMiddle && !isRing && !isPinky) {
    return 'rock';
  }

  // Paper: all 4 fingers extended open
  if (isIndex && isMiddle && isRing && isPinky) {
    return 'paper';
  }

  // Scissors: Index & Middle extended, Ring & Pinky curled
  if (isIndex && isMiddle && !isRing && !isPinky) {
    return 'scissors';
  }

  return 'waiting';
}

// ============================================================================
// 7. Fast 2D HUD Rendering (Zero Gaussian Blur Overhead!)
// ============================================================================
function drawSkeleton(ctx, pts) {
  if (!state.showSkeleton) return;

  ctx.lineWidth = 2;
  ctx.strokeStyle = state.appMode === 'rps' ? 'rgba(217, 70, 239, 0.45)' : 'rgba(0, 242, 254, 0.4)';

  ctx.beginPath();
  for (let i = 0; i < CONFIG.skeletonConnections.length; i++) {
    const conn = CONFIG.skeletonConnections[i];
    const p1 = pts[conn[0]];
    const p2 = pts[conn[1]];
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);
  }
  ctx.stroke();

  ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
  for (let i = 0; i < 21; i++) {
    if (i === 8 || i === 4) continue;
    const p = pts[i];
    ctx.fillRect(p.x - 2, p.y - 2, 4, 4);
  }
}

function drawPointerReticle(ctx, tipPoint, gesture) {
  const isTapping = gesture.type === 'thumb_tap';
  const isScrolling = gesture.type === 'scrolling';

  let color = '#00f2fe';
  if (isTapping) color = '#00ff87';
  if (isScrolling) color = '#a855f7';
  if (!state.active) color = '#ef4444';

  const radius = isTapping ? 18 : 14;

  ctx.lineWidth = isTapping ? 2.5 : 1.8;
  ctx.strokeStyle = color;
  ctx.beginPath();
  ctx.arc(tipPoint.x, tipPoint.y, radius, 0, Math.PI * 2);
  ctx.stroke();

  const gap = 5;
  const len = 7;
  ctx.beginPath();
  ctx.moveTo(tipPoint.x, tipPoint.y - radius - len);
  ctx.lineTo(tipPoint.x, tipPoint.y - radius + gap);
  ctx.moveTo(tipPoint.x, tipPoint.y + radius + len);
  ctx.lineTo(tipPoint.x, tipPoint.y + radius - gap);
  ctx.moveTo(tipPoint.x - radius - len, tipPoint.y);
  ctx.lineTo(tipPoint.x - radius + gap, tipPoint.y);
  ctx.moveTo(tipPoint.x + radius + len, tipPoint.y);
  ctx.lineTo(tipPoint.x + radius - gap, tipPoint.y);
  ctx.stroke();

  ctx.fillStyle = isTapping ? '#00ff87' : '#ffffff';
  ctx.beginPath();
  ctx.arc(tipPoint.x, tipPoint.y, isTapping ? 4.5 : 3, 0, Math.PI * 2);
  ctx.fill();

  ctx.font = '11px "JetBrains Mono", monospace';
  ctx.fillStyle = color;
  const tag = isTapping ? 'CLICK' : isScrolling ? 'SCROLL' : 'INDEX MOUSE';
  ctx.fillText(tag, tipPoint.x + radius + 10, tipPoint.y - 4);

  if (gesture.thumbPoint) {
    const thumbPt = gesture.thumbPoint;
    ctx.lineWidth = isTapping ? 2.5 : 1.5;
    ctx.strokeStyle = isTapping ? '#00ff87' : 'rgba(255, 183, 0, 0.8)';
    ctx.beginPath();
    ctx.arc(thumbPt.x, thumbPt.y, isTapping ? 8 : 5, 0, Math.PI * 2);
    ctx.stroke();

    if (isTapping) {
      ctx.fillStyle = 'rgba(0, 255, 135, 0.5)';
      ctx.fill();
    }
  }
}

function drawClutchStatusOverlay(ctx, width, height, gestureType) {
  if (state.trackingMode !== 'relative') return;

  const isClutched = gestureType === 'clutch' || gestureType === 'standby';
  ctx.font = '12px "JetBrains Mono", monospace';
  ctx.textAlign = 'center';

  if (isClutched) {
    ctx.fillStyle = 'rgba(255, 183, 0, 0.9)';
    ctx.fillText('✋ CLUTCH ENGAGED • REPOSITION HAND (CURSOR FROZEN)', width / 2, 32);
  } else if (state.isPointingEngaged) {
    ctx.fillStyle = 'rgba(0, 255, 135, 0.9)';
    ctx.fillText('🔒 RELATIVE TRACKING ACTIVE • POINT TO MOVE • TAP THUMB TO CLICK', width / 2, 32);
  }
}

function addClickRipple(x, y) {
  state.clickRipples.push({ x, y, radius: 6, maxRadius: 36, alpha: 1.0 });
}

function updateAndDrawRipples(ctx) {
  ctx.lineWidth = 2;
  for (let i = state.clickRipples.length - 1; i >= 0; i--) {
    const r = state.clickRipples[i];
    ctx.strokeStyle = `rgba(0, 255, 135, ${r.alpha})`;
    ctx.beginPath();
    ctx.arc(r.x, r.y, r.radius, 0, Math.PI * 2);
    ctx.stroke();

    r.radius += 3;
    r.alpha -= 0.08;
    if (r.alpha <= 0) {
      state.clickRipples.splice(i, 1);
    }
  }
}

// ============================================================================
// 8. Main Frame Processing Loop
// ============================================================================
let firstFrameProcessed = false;

function onResults(results) {
  if (!firstFrameProcessed) {
    firstFrameProcessed = true;
    if (loadingOverlay) {
      loadingOverlay.style.opacity = '0';
      setTimeout(() => { loadingOverlay.style.display = 'none'; }, 300);
    }
  }

  resizeCanvas();
  const width = (outputCanvas.width && outputCanvas.width > 50) ? outputCanvas.width : 1280;
  const height = (outputCanvas.height && outputCanvas.height > 50) ? outputCanvas.height : 720;
  const now = performance.now();
  const isHidden = document.hidden || outputCanvas.width <= 50;

  // Throttled FPS calculation
  state.frameCount++;
  if (now - state.lastFpsUpdate >= 500) {
    state.fps = Math.round((state.frameCount * 1000) / (now - state.lastFpsUpdate));
    if (fpsValue) fpsValue.textContent = state.fps;
    state.frameCount = 0;
    state.lastFpsUpdate = now;
  }

  // Draw Camera Feed
  if (!isHidden) {
    outCtx.save();
    outCtx.clearRect(0, 0, width, height);
    if (state.mirror) {
      outCtx.translate(width, 0);
      outCtx.scale(-1, 1);
    }
    outCtx.drawImage(results.image, 0, 0, width, height);
    outCtx.restore();

    outCtx.fillStyle = state.appMode === 'rps' ? 'rgba(10, 8, 24, 0.35)' : 'rgba(6, 9, 18, 0.25)';
    outCtx.fillRect(0, 0, width, height);
  }

  const hasHands = results.multiHandLandmarks && results.multiHandLandmarks.length > 0;

  if (hasHands) {
    const raw = results.multiHandLandmarks[0];

    // Zero-allocation landmark filtering
    for (let i = 0; i < 21; i++) {
      handFilters[i].filter(raw[i], now, filteredNormPoints[i]);
      let x = filteredNormPoints[i].x;
      if (state.mirror) x = 1.0 - x;
      smoothedPoints[i].x = x * width;
      smoothedPoints[i].y = filteredNormPoints[i].y * height;
      smoothedPoints[i].z = filteredNormPoints[i].z;
    }

    if (!isHidden) {
      drawSkeleton(outCtx, smoothedPoints);
    }

    // ========================================================================
    // MODE A: ROCK-PAPER-SCISSORS BATTLE ARENA
    // ========================================================================
    if (state.appMode === 'rps') {
      const rpsPose = classifyRPS(raw);
      processRpsFrame(rpsPose, now);
    }
    // ========================================================================
    // MODE B: VIRTUAL MOUSE PC CONTROLLER
    // ========================================================================
    else {
      let filteredIndexNormX = filteredNormPoints[8].x;
      if (state.mirror) filteredIndexNormX = 1.0 - filteredIndexNormX;
      const filteredIndexNormY = filteredNormPoints[8].y;

      const gesture = classifyMouseGestures(raw, smoothedPoints);
      state.gestureState = gesture.type;

      if (now - state.lastUiUpdate > 80) {
        updateMouseGestureUI(gesture);
        state.lastUiUpdate = now;
      }

      if (!isHidden) {
        drawClutchStatusOverlay(outCtx, width, height, gesture.type);
      }

      if (gesture.type === 'pointing' || gesture.type === 'thumb_tap') {
        const indexTip = smoothedPoints[8];
        if (!isHidden) {
          drawPointerReticle(outCtx, indexTip, gesture);
        }

        if (state.trackingMode === 'relative') {
          if (!state.isPointingEngaged || !state.lastTrackedIndexPos) {
            state.isPointingEngaged = true;
            state.lastTrackedIndexPos = { x: filteredIndexNormX, y: filteredIndexNormY };
          } else {
            const dxNorm = filteredIndexNormX - state.lastTrackedIndexPos.x;
            const dyNorm = filteredIndexNormY - state.lastTrackedIndexPos.y;
            state.lastTrackedIndexPos.x = filteredIndexNormX;
            state.lastTrackedIndexPos.y = filteredIndexNormY;

            if (Math.abs(dxNorm) > 0.0005 || Math.abs(dyNorm) > 0.0005) {
              const speedFactor = state.sensitivity * 2.2;
              const dx = dxNorm * state.screenWidth * speedFactor;
              const dy = dyNorm * state.screenHeight * speedFactor;

              state.cursorX = Math.max(0, Math.min(state.screenWidth, state.cursorX + dx));
              state.cursorY = Math.max(0, Math.min(state.screenHeight, state.cursorY + dy));

              const targetX = Math.round(state.cursorX);
              const targetY = Math.round(state.cursorY);
              if (targetX !== state.lastSentX || targetY !== state.lastSentY) {
                state.lastSentX = targetX;
                state.lastSentY = targetY;
                if (state.active && window.mouseAPI) {
                  window.mouseAPI.sendMove(targetX, targetY);
                }
              }
            }
          }
        } else {
          const reachFrac = state.reach / 100.0;
          const halfReach = reachFrac / 2.0;
          let relX = (filteredIndexNormX - (0.5 - halfReach)) / reachFrac;
          let relY = (filteredIndexNormY - (0.5 - halfReach)) / reachFrac;
          relX = Math.max(0, Math.min(1, 0.5 + (relX - 0.5) * state.sensitivity));
          relY = Math.max(0, Math.min(1, 0.5 + (relY - 0.5) * state.sensitivity));
          state.cursorX = relX * state.screenWidth;
          state.cursorY = relY * state.screenHeight;

          const targetX = Math.round(state.cursorX);
          const targetY = Math.round(state.cursorY);
          if (targetX !== state.lastSentX || targetY !== state.lastSentY) {
            state.lastSentX = targetX;
            state.lastSentY = targetY;
            if (state.active && window.mouseAPI) {
              window.mouseAPI.sendMove(targetX, targetY);
            }
          }
        }

        // Thumb Tap (Atomic Single Click)
        if (gesture.isThumbTapping && !state.isThumbTapping) {
          state.isThumbTapping = true;
          sound.playClick();
          addClickRipple(smoothedPoints[4].x, smoothedPoints[4].y);
          if (state.active && window.mouseAPI) {
            window.mouseAPI.sendAction('CLICK');
          }
        } else if (!gesture.isThumbTapping && state.isThumbTapping) {
          state.isThumbTapping = false;
        }

        state.isScrolling = false;
        state.lastScrollY = null;

      } else if (gesture.type === 'scrolling') {
        const avgY = (smoothedPoints[12].y + smoothedPoints[8].y) / 2;
        const avgX = (smoothedPoints[12].x + smoothedPoints[8].x) / 2;

        if (!isHidden) {
          drawPointerReticle(outCtx, { x: avgX, y: avgY }, gesture);
        }

        if (state.lastScrollY !== null) {
          const deltaY = avgY - state.lastScrollY;
          if (Math.abs(deltaY) > 2) {
            const scrollStep = -deltaY * 12;
            if (state.active && window.mouseAPI) {
              window.mouseAPI.sendAction('W', scrollStep);
            }
          }
        }
        state.lastScrollY = avgY;
        state.isThumbTapping = false;

      } else {
        state.isPointingEngaged = false;
        state.lastTrackedIndexPos = null;
        state.isThumbTapping = false;
        state.lastScrollY = null;
      }
    }
  } else {
    state.isPointingEngaged = false;
    state.lastTrackedIndexPos = null;
    state.isThumbTapping = false;

    if (state.appMode === 'rps') {
      rpsPlayerIcon.textContent = '❓';
      rpsPlayerMoveText.textContent = 'NO HAND DETECTED';
      gestureValue.textContent = 'Show Hand in Camera';
      gestureDot.className = 'dot warning';
    } else {
      if (gestureValue) {
        gestureValue.textContent = 'Searching Hand...';
        gestureDot.className = 'dot warning';
      }
    }

    for (let i = 0; i < 21; i++) handFilters[i].reset();
  }

  if (!isHidden) {
    updateAndDrawRipples(outCtx);
  }
}

// ============================================================================
// 9. Rock Paper Scissors Instant Counter Engine
// ============================================================================
function triggerClashPulse() {
  if (!rpsAiCard || !rpsPlayerCard) return;
  rpsAiCard.classList.remove('pulse-clash');
  rpsPlayerCard.classList.remove('pulse-clash');
  void rpsAiCard.offsetWidth; // Force reflow
  rpsAiCard.classList.add('pulse-clash');
  rpsPlayerCard.classList.add('pulse-clash');
}

function processRpsFrame(playerMove, now) {
  const previousMove = state.rpsPlayerMove;
  state.rpsPlayerMove = playerMove;

  // 1. Update Player HUD Card
  if (playerMove !== 'waiting') {
    rpsPlayerIcon.textContent = RPS_ICONS[playerMove];
    rpsPlayerMoveText.textContent = playerMove.toUpperCase();
    if (gestureValue) gestureValue.textContent = `Player: ${playerMove.toUpperCase()}`;
    if (gestureDot) {
      gestureDot.className = 'dot active';
      gestureDot.style.background = '#00f2fe';
    }
  } else {
    rpsPlayerIcon.textContent = '❓';
    rpsPlayerMoveText.textContent = 'SHOW ✊, ✋, OR ✌️';
    if (gestureValue) gestureValue.textContent = 'Detecting RPS Gesture...';
    if (gestureDot) {
      gestureDot.className = 'dot warning';
      gestureDot.style.background = '#ffb700';
    }
  }

  // 2. INSTANT MIND-READER MODE (Unbeatable Instant Counter)
  if (state.rpsMode === 'instant') {
    if (playerMove !== 'waiting') {
      if (playerMove !== previousMove) {
        // Player switched pose!
        state.rpsPoseStartTime = now;
        state.rpsAiMove = COUNTER_MAP[playerMove];
        state.rpsScores.ai++;
        state.rpsStreak++;

        sound.playMoveChange();
        triggerClashPulse();

        // Update scoreboard
        if (rpsScoreAi) rpsScoreAi.textContent = state.rpsScores.ai;
        if (rpsStreakBadge) rpsStreakBadge.textContent = `⚡ ${state.rpsStreak} COUNTERED`;

        // Pick dynamic AI taunt
        const taunt = TAUNTS[Math.floor(Math.random() * TAUNTS.length)];
        if (rpsAiTaunt) rpsAiTaunt.textContent = `"${taunt}"`;
      }

      // Live latency readout
      const latency = Math.max(4, Math.round(now - state.rpsPoseStartTime));
      const latencyText = `${latency}ms`;
      if (rpsReactionVal) rpsReactionVal.textContent = latencyText;
      if (rpsLatencyMetric) rpsLatencyMetric.textContent = latencyText;

      // Update AI Card
      if (rpsAiIcon) rpsAiIcon.textContent = RPS_ICONS[state.rpsAiMove];
      if (rpsAiMoveText) rpsAiMoveText.textContent = state.rpsAiMove.toUpperCase();

      // Show Result Toast
      let counterDesc = 'COVERS';
      if (state.rpsAiMove === 'scissors') counterDesc = 'SLICES';
      if (state.rpsAiMove === 'rock') counterDesc = 'CRUSHES';

      if (rpsResultToast) {
        rpsResultToast.textContent = `⚡ AI ${state.rpsAiMove.toUpperCase()} ${counterDesc} YOUR ${playerMove.toUpperCase()}!`;
        rpsResultToast.className = 'match-result-toast loss';
      }
    } else {
      if (rpsAiIcon) rpsAiIcon.textContent = '🤖';
      if (rpsAiMoveText) rpsAiMoveText.textContent = 'AWAITING MOVE...';
      if (rpsResultToast) {
        rpsResultToast.textContent = '⚡ SHOW ROCK, PAPER, OR SCISSORS';
        rpsResultToast.className = 'match-result-toast';
      }
    }
  }
  // 3. TOURNAMENT 3-2-1 MATCH MODE
  else if (state.rpsMode === 'tournament') {
    if (state.rpsTournamentState === 'idle') {
      if (rpsAiIcon) rpsAiIcon.textContent = '🤖';
      if (rpsAiMoveText) rpsAiMoveText.textContent = 'READY FOR ROUND';
    }
  }
}

// Tournament 3-2-1 Match Countdown
function startTournamentRound() {
  if (state.rpsTournamentState === 'counting') return;

  state.rpsTournamentState = 'counting';
  state.rpsCountdownVal = 3;
  if (rpsCountdownOrb) {
    rpsCountdownOrb.style.display = 'block';
    rpsCountdownOrb.textContent = '3';
  }
  if (rpsVsEmblem) rpsVsEmblem.style.display = 'none';
  if (rpsResultToast) {
    rpsResultToast.textContent = 'GET READY...';
    rpsResultToast.className = 'match-result-toast';
  }
  if (rpsAiIcon) rpsAiIcon.textContent = '⚡';
  if (rpsAiMoveText) rpsAiMoveText.textContent = 'HOLDING MOVE...';

  sound.playCountdownBeep(3);

  clearInterval(state.rpsCountdownTimer);
  state.rpsCountdownTimer = setInterval(() => {
    state.rpsCountdownVal--;

    if (state.rpsCountdownVal > 0) {
      if (rpsCountdownOrb) rpsCountdownOrb.textContent = String(state.rpsCountdownVal);
      sound.playCountdownBeep(state.rpsCountdownVal);
    } else if (state.rpsCountdownVal === 0) {
      if (rpsCountdownOrb) rpsCountdownOrb.textContent = 'SHOOT!';
      sound.playCountdownBeep(0);

      // Evaluate Round Outcome at SHOOT!
      evaluateTournamentOutcome();
    } else {
      clearInterval(state.rpsCountdownTimer);
      if (rpsCountdownOrb) rpsCountdownOrb.style.display = 'none';
      if (rpsVsEmblem) rpsVsEmblem.style.display = 'block';
      state.rpsTournamentState = 'idle';
    }
  }, 750);
}

function evaluateTournamentOutcome() {
  const pMove = state.rpsPlayerMove !== 'none' && state.rpsPlayerMove !== 'waiting' ? state.rpsPlayerMove : 'rock';
  
  // Competitive AI move selection (65% counter, 35% random)
  let aiMove;
  if (Math.random() < 0.65) {
    aiMove = COUNTER_MAP[pMove]; // Counter
  } else {
    const moves = ['rock', 'paper', 'scissors'];
    aiMove = moves[Math.floor(Math.random() * moves.length)];
  }

  state.rpsAiMove = aiMove;
  if (rpsAiIcon) rpsAiIcon.textContent = RPS_ICONS[aiMove];
  if (rpsAiMoveText) rpsAiMoveText.textContent = aiMove.toUpperCase();
  triggerClashPulse();

  // Determine Winner
  if (pMove === aiMove) {
    // Draw
    state.rpsScores.draws++;
    if (rpsResultToast) {
      rpsResultToast.textContent = `🤝 TIE! BOTH CHOSE ${pMove.toUpperCase()}`;
      rpsResultToast.className = 'match-result-toast draw';
    }
    sound.playClick();
  } else if (COUNTER_MAP[pMove] === aiMove) {
    // AI Wins
    state.rpsScores.ai++;
    state.rpsStreak = 0;
    if (rpsResultToast) {
      rpsResultToast.textContent = `💥 AI WINS! ${aiMove.toUpperCase()} BEATS ${pMove.toUpperCase()}`;
      rpsResultToast.className = 'match-result-toast loss';
    }
    sound.playDefeatTone();
  } else {
    // Player Wins!
    state.rpsScores.player++;
    state.rpsStreak++;
    if (rpsResultToast) {
      rpsResultToast.textContent = `🎉 YOU WIN! ${pMove.toUpperCase()} BEATS ${aiMove.toUpperCase()}`;
      rpsResultToast.className = 'match-result-toast win';
    }
    sound.playVictoryFanfare();
  }

  // Update Scoreboard DOM
  if (rpsScorePlayer) rpsScorePlayer.textContent = state.rpsScores.player;
  if (rpsScoreAi) rpsScoreAi.textContent = state.rpsScores.ai;
  if (rpsScoreDraw) rpsScoreDraw.textContent = state.rpsScores.draws;
  if (rpsStreakBadge) rpsStreakBadge.textContent = `🔥 ${state.rpsStreak} STREAK`;
}

function resetRpsScores() {
  state.rpsScores = { player: 0, ai: 0, draws: 0 };
  state.rpsStreak = 0;
  if (rpsScorePlayer) rpsScorePlayer.textContent = '0';
  if (rpsScoreAi) rpsScoreAi.textContent = '0';
  if (rpsScoreDraw) rpsScoreDraw.textContent = '0';
  if (rpsStreakBadge) rpsStreakBadge.textContent = state.rpsMode === 'instant' ? '⚡ 0 COUNTERED' : '🔥 0 STREAK';
  if (rpsResultToast) {
    rpsResultToast.textContent = 'SCORES RESET • READY';
    rpsResultToast.className = 'match-result-toast';
  }
  sound.playClick();
}


// ============================================================================
// 10. UI Mode Navigation & Virtual Mouse Event Handlers
// ============================================================================
function setAppMode(mode) {
  state.appMode = mode;
  sound.playToggle(true);

  if (mode === 'rps') {
    tabBtnRPS.classList.add('active');
    tabBtnMouse.classList.remove('active');

    mouseSettingsDeck.style.display = 'none';
    rpsSettingsDeck.style.display = 'block';
    rpsArenaOverlay.style.display = 'flex';
    screenBoxLabel.style.display = 'none';
    gestureHintsBar.style.display = 'none';

    masterToggleBtn.style.display = 'none';
    coordValue.parentElement.style.display = 'none';

    brandSubtitle.textContent = 'AI Rock Paper Scissors Battle Arena';
    footerModeText.innerHTML = 'Mode: <strong class="glow-text" style="color: #ff007f;">RPS Battle Active</strong>';

    // Safely pause virtual mouse
    state.isPointingEngaged = false;
  } else {
    clearInterval(state.rpsCountdownTimer);
    if (rpsCountdownOrb) rpsCountdownOrb.style.display = 'none';
    if (rpsVsEmblem) rpsVsEmblem.style.display = 'block';
    state.rpsTournamentState = 'idle';

    tabBtnMouse.classList.add('active');
    tabBtnRPS.classList.remove('active');

    mouseSettingsDeck.style.display = 'block';
    rpsSettingsDeck.style.display = 'none';
    rpsArenaOverlay.style.display = 'none';
    screenBoxLabel.style.display = 'block';
    gestureHintsBar.style.display = 'flex';

    masterToggleBtn.style.display = 'flex';
    coordValue.parentElement.style.display = 'flex';

    brandSubtitle.textContent = 'AI Optical Hand Virtual Mouse for Windows';
    footerModeText.innerHTML = 'Mode: <strong class="glow-text">Virtual Mouse Active</strong>';
  }
}

tabBtnMouse.addEventListener('click', () => setAppMode('mouse'));
tabBtnRPS.addEventListener('click', () => setAppMode('rps'));

// RPS Mode Toggle (Instant vs Tournament)
rpsModeInstant.addEventListener('click', () => {
  state.rpsMode = 'instant';
  rpsModeInstant.classList.add('active');
  rpsModeInstant.style.background = 'rgba(0, 242, 254, 0.15)';
  rpsModeInstant.style.borderColor = 'var(--accent-cyan)';
  rpsModeInstant.style.color = 'var(--accent-cyan)';

  rpsModeTournament.classList.remove('active');
  rpsModeTournament.style.background = 'rgba(255, 255, 255, 0.05)';
  rpsModeTournament.style.borderColor = 'var(--border-subtle)';
  rpsModeTournament.style.color = 'var(--text-secondary)';

  rpsTournamentControls.style.display = 'none';
  rpsVsEmblem.style.display = 'block';
  rpsCountdownOrb.style.display = 'none';
  rpsResultToast.textContent = '⚡ SHOW ROCK, PAPER, OR SCISSORS';
});

rpsModeTournament.addEventListener('click', () => {
  state.rpsMode = 'tournament';
  rpsModeTournament.classList.add('active');
  rpsModeTournament.style.background = 'rgba(0, 242, 254, 0.15)';
  rpsModeTournament.style.borderColor = 'var(--accent-cyan)';
  rpsModeTournament.style.color = 'var(--accent-cyan)';

  rpsModeInstant.classList.remove('active');
  rpsModeInstant.style.background = 'rgba(255, 255, 255, 0.05)';
  rpsModeInstant.style.borderColor = 'var(--border-subtle)';
  rpsModeInstant.style.color = 'var(--text-secondary)';

  rpsTournamentControls.style.display = 'block';
  rpsResultToast.textContent = 'PRESS START ROUND OR SPACE';
});

rpsStartRoundBtn.addEventListener('click', startTournamentRound);
rpsResetScoreBtn.addEventListener('click', resetRpsScores);

function updateMouseGestureUI(gesture) {
  if (!gestureValue) return;

  gestureValue.textContent = gesture.label;

  if (gesture.type === 'pointing') {
    gestureDot.className = 'dot active';
    gestureDot.style.background = '#00f2fe';
  } else if (gesture.type === 'thumb_tap') {
    gestureDot.className = 'dot active';
    gestureDot.style.background = '#00ff87';
  } else if (gesture.type === 'scrolling') {
    gestureDot.className = 'dot active';
    gestureDot.style.background = '#a855f7';
  } else if (gesture.type === 'clutch') {
    gestureDot.className = 'dot warning';
    gestureDot.style.background = '#ffb700';
  } else {
    gestureDot.className = 'dot warning';
    gestureDot.style.background = '#94a3b8';
  }

  if (coordValue) coordValue.textContent = `${Math.round(state.cursorX)}, ${Math.round(state.cursorY)}`;
  if (miniStatusText) {
    miniStatusText.textContent = state.active ? gesture.label : 'PAUSED (F8)';
  }
}

function setMasterTracking(active) {
  state.active = active;
  sound.playToggle(active);

  if (active) {
    masterToggleBtn.className = 'master-pill active';
    masterToggleText.textContent = 'MOUSE ACTIVE (F8)';
    masterToggleSwitch.checked = true;
    trackingIndicatorText.textContent = 'Controlling Windows Cursor';
    trackingIndicatorText.parentElement.style.color = 'var(--accent-green)';
    if (miniDot) miniDot.className = 'mini-dot active';
  } else {
    masterToggleBtn.className = 'master-pill paused';
    masterToggleText.textContent = 'MOUSE PAUSED (F8)';
    masterToggleSwitch.checked = false;
    trackingIndicatorText.textContent = 'Virtual Mouse Suspended';
    trackingIndicatorText.parentElement.style.color = 'var(--accent-red)';
    if (miniDot) miniDot.className = 'mini-dot paused';
  }
}

masterToggleBtn.addEventListener('click', () => setMasterTracking(!state.active));
masterToggleSwitch.addEventListener('change', (e) => setMasterTracking(e.target.checked));

modeRelativeBtn.addEventListener('click', () => {
  state.trackingMode = 'relative';
  modeRelativeBtn.classList.add('active');
  modeRelativeBtn.style.background = 'rgba(0, 242, 254, 0.15)';
  modeRelativeBtn.style.borderColor = 'var(--accent-cyan)';
  modeRelativeBtn.style.color = 'var(--accent-cyan)';

  modeAbsoluteBtn.classList.remove('active');
  modeAbsoluteBtn.style.background = 'rgba(255, 255, 255, 0.05)';
  modeAbsoluteBtn.style.borderColor = 'var(--border-subtle)';
  modeAbsoluteBtn.style.color = 'var(--text-secondary)';

  reachRow.style.display = 'none';
  screenBoxLabel.textContent = 'Relative Clutched Tracking • Open Palm to Reposition';
});

modeAbsoluteBtn.addEventListener('click', () => {
  state.trackingMode = 'absolute';
  modeAbsoluteBtn.classList.add('active');
  modeAbsoluteBtn.style.background = 'rgba(0, 242, 254, 0.15)';
  modeAbsoluteBtn.style.borderColor = 'var(--accent-cyan)';
  modeAbsoluteBtn.style.color = 'var(--accent-cyan)';

  modeRelativeBtn.classList.remove('active');
  modeRelativeBtn.style.background = 'rgba(255, 255, 255, 0.05)';
  modeRelativeBtn.style.borderColor = 'var(--border-subtle)';
  modeRelativeBtn.style.color = 'var(--text-secondary)';

  reachRow.style.display = 'flex';
  screenBoxLabel.textContent = 'Active Tracking Zone (Mapped to PC Monitor)';
});

smoothingLevelInput.addEventListener('input', (e) => {
  state.smoothingLevel = parseInt(e.target.value);
  const preset = CONFIG.smoothingPresets[state.smoothingLevel];
  smoothingVal.textContent = preset.name;

  filterMetrics.innerHTML = `
    <span>Cutoff: <strong>${preset.cutoffText}</strong></span>
    <span>Beta: <strong>${preset.betaText}</strong></span>
    <span>Lag: <strong>${preset.lagText}</strong></span>
  `;

  document.querySelectorAll('.ticks-row .tick').forEach((tick, idx) => {
    tick.classList.toggle('active', idx + 1 === state.smoothingLevel);
  });

  for (let i = 0; i < 21; i++) {
    handFilters[i].setParams(preset.minCutoff, preset.beta);
  }
});

sensitivityInput.addEventListener('input', (e) => {
  state.sensitivity = parseFloat(e.target.value);
  sensitivityVal.textContent = `${state.sensitivity.toFixed(1)}x`;
});

thumbTapInput.addEventListener('input', (e) => {
  state.thumbTapThreshold = parseFloat(e.target.value);
  let label = 'Normal';
  if (state.thumbTapThreshold < 0.26) label = 'Close Tap';
  if (state.thumbTapThreshold > 0.38) label = 'Easy Tap';
  thumbTapVal.textContent = `${label} (${state.thumbTapThreshold.toFixed(2)})`;
});

reachInput.addEventListener('input', (e) => {
  state.reach = parseInt(e.target.value);
  reachVal.textContent = `Normal (${state.reach}%)`;
});

toggleSkeleton.addEventListener('change', (e) => state.showSkeleton = e.target.checked);
toggleScreenBox.addEventListener('change', (e) => state.showScreenBox = e.target.checked);
toggleMirror.addEventListener('change', (e) => state.mirror = e.target.checked);
toggleSound.addEventListener('change', (e) => {
  state.sound = e.target.checked;
  sound.enabled = state.sound;
});

function toggleMiniMode(enable) {
  state.isMiniMode = enable !== undefined ? enable : !state.isMiniMode;
  appContainer.classList.toggle('mini-mode', state.isMiniMode);
  if (window.mouseAPI && window.mouseAPI.toggleMiniMode) {
    window.mouseAPI.toggleMiniMode(state.isMiniMode);
  }
  setTimeout(resizeCanvas, 80);
}

toggleMiniBtn.addEventListener('click', () => toggleMiniMode(true));
miniHudActionBtn.addEventListener('click', () => toggleMiniMode(true));
miniRestoreBtn.addEventListener('click', () => toggleMiniMode(false));

testClickBtn.addEventListener('click', () => {
  sound.playClick();
  testClickBtn.textContent = '🎉 Click Registered!';
  setTimeout(() => {
    testClickBtn.innerHTML = `
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M15 15l5 5m-5-5a5 5 0 1 0-7.07-7.07 5 5 0 0 0 7.07 7.07z"/>
      </svg>
      Test Click Target
    `;
  }, 1000);
});

// Keyboard Hotkeys
window.addEventListener('keydown', (e) => {
  if (e.key === 'Tab') {
    e.preventDefault();
    setAppMode(state.appMode === 'mouse' ? 'rps' : 'mouse');
  } else if (e.code === 'Space') {
    if (state.appMode === 'rps') {
      e.preventDefault();
      if (state.rpsMode === 'tournament') {
        startTournamentRound();
      }
    } else {
      e.preventDefault();
      setMasterTracking(!state.active);
    }
  } else if (e.key === 'F8') {
    e.preventDefault();
    setMasterTracking(!state.active);
  } else if (e.key === 'p' || e.key === 'P') {
    toggleMiniMode();
  }
});

if (window.mouseAPI && window.mouseAPI.onGlobalToggle) {
  window.mouseAPI.onGlobalToggle((activeState) => {
    setMasterTracking(activeState);
  });
}

// ============================================================================
// 11. Startup & Initialization
// ============================================================================
async function startApp() {
  sound.init();

  if (window.mouseAPI) {
    try {
      const screenSize = await window.mouseAPI.getScreenSize();
      if (screenSize && screenSize.width) {
        state.screenWidth = screenSize.width;
        state.screenHeight = screenSize.height;
        state.cursorX = Math.round(state.screenWidth / 2);
        state.cursorY = Math.round(state.screenHeight / 2);
      }
    } catch (e) {}

    try {
      const pt = await window.mouseAPI.getCursorPos();
      if (pt && typeof pt.x === 'number') {
        state.cursorX = pt.x;
        state.cursorY = pt.y;
      }
    } catch (e) {}
  }

  const loadingText = document.querySelector('.loading-text');

  if (typeof Hands === 'undefined') {
    loadingOverlay.innerHTML = `
      <div style="color: #ef4444; font-size: 2rem;">⚠️</div>
      <div class="loading-text" style="color: #fca5a5;">MediaPipe AI Model Unavailable</div>
      <div class="loading-sub">Check internet connection and restart app.</div>
    `;
    return;
  }

  if (loadingText) loadingText.textContent = 'Connecting Camera (60 FPS Mode)...';
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        frameRate: { ideal: 60, min: 30 },
        facingMode: 'user'
      },
      audio: false
    });
    videoElement.srcObject = stream;
    await videoElement.play();
  } catch (err) {
    console.error('Camera error:', err);
    loadingOverlay.innerHTML = `
      <div style="color: #ef4444; font-size: 2rem;">⚠️</div>
      <div class="loading-text" style="color: #fca5a5;">Camera Unavailable</div>
      <div class="loading-sub">${err.message || 'Check camera permissions.'}</div>
    `;
    return;
  }

  if (loadingText) loadingText.textContent = 'Initializing Ultra-Fast AI Model...';

  const hands = new Hands({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
  });

  hands.setOptions({
    maxNumHands: 1,
    modelComplexity: 0,
    minDetectionConfidence: 0.6,
    minTrackingConfidence: 0.6
  });

  hands.onResults(onResults);

  let isSending = false;
  async function pumpFrame() {
    if (isSending || videoElement.readyState < 2) return;
    isSending = true;
    try {
      await hands.send({ image: videoElement });
    } catch (e) {}
    isSending = false;
  }

  setInterval(pumpFrame, 16);
}

window.addEventListener('DOMContentLoaded', () => {
  resizeCanvas();
  startApp();
});
