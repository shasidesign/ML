/* StyleIQ — Premium Subtle Particle System */
(function () {
  const canvas = document.getElementById('particles');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, particles = [], orbs = [];

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  // Subtle floating particles
  function Particle() {
    this.x = Math.random() * W;
    this.y = Math.random() * H;
    this.size = Math.random() * 1.2 + 0.2;
    this.opacity = Math.random() * 0.35 + 0.05;
    this.speedX = (Math.random() - .5) * .25;
    this.speedY = (Math.random() - .5) * .25;
    this.twinkle = Math.random() * .008 + .003;
    this.twinkleDir = Math.random() > .5 ? 1 : -1;
    const r = Math.random();
    this.color = r > .6 ? '#818cf8' : r > .3 ? '#22d3ee' : '#c084fc';
  }
  Particle.prototype.update = function() {
    this.x += this.speedX;
    this.y += this.speedY;
    this.opacity += this.twinkle * this.twinkleDir;
    if (this.opacity > .4 || this.opacity < .03) this.twinkleDir *= -1;
    if (this.x < 0) this.x = W;
    if (this.x > W) this.x = 0;
    if (this.y < 0) this.y = H;
    if (this.y > H) this.y = 0;
  };
  Particle.prototype.draw = function() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fillStyle = this.color;
    ctx.globalAlpha = this.opacity;
    ctx.fill();
  };

  // Soft glowing orbs
  function Orb() {
    this.x = Math.random() * W;
    this.y = Math.random() * H;
    this.r = Math.random() * 180 + 80;
    this.opacity = Math.random() * .04 + .01;
    this.speedX = (Math.random() - .5) * .15;
    this.speedY = (Math.random() - .5) * .15;
    const r = Math.random();
    this.color = r > .5 ? '99,102,241' : r > .25 ? '168,85,247' : '34,211,238';
  }
  Orb.prototype.update = function() {
    this.x += this.speedX;
    this.y += this.speedY;
    if (this.x < -this.r) this.x = W + this.r;
    if (this.x > W + this.r) this.x = -this.r;
    if (this.y < -this.r) this.y = H + this.r;
    if (this.y > H + this.r) this.y = -this.r;
  };
  Orb.prototype.draw = function() {
    const g = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.r);
    g.addColorStop(0, `rgba(${this.color},${this.opacity})`);
    g.addColorStop(1, `rgba(${this.color},0)`);
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
    ctx.fillStyle = g;
    ctx.globalAlpha = 1;
    ctx.fill();
  };

  function connectNearby() {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const d  = Math.sqrt(dx*dx + dy*dy);
        if (d < 100) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = '#818cf8';
          ctx.globalAlpha = (1 - d/100) * .05;
          ctx.lineWidth = .5;
          ctx.stroke();
        }
      }
    }
  }

  function init() {
    resize();
    particles = Array.from({ length: 50 }, () => new Particle());
    orbs      = Array.from({ length: 5  }, () => new Orb());
  }

  function animate() {
    ctx.clearRect(0, 0, W, H);
    orbs.forEach(o => { o.update(); o.draw(); });
    particles.forEach(p => { p.update(); p.draw(); });
    connectNearby();
    ctx.globalAlpha = 1;
    requestAnimationFrame(animate);
  }

  window.addEventListener('resize', () => { resize(); });
  init();
  animate();
})();
