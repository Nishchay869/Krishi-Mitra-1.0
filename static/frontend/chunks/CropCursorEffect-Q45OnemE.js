import{a as e}from"./rolldown-runtime-B0Z9INg1.js";import{r as t}from"./react-D_UK1nbl.js";var n=e(t(),1),r=220,i=800,a=700,o=2e3,s=600,c=[`🌾`,`🌱`,`🫘`,`🌽`,`🍃`,`🌿`,`🌻`],l=[`🌱`,`🌿`,`🌾`,`🍀`,`🪴`],u=(e,t)=>e+Math.random()*(t-e),d=`km-crop-cursor-styles`;function f(){if(document.getElementById(d))return;let e=document.createElement(`style`);e.id=d,e.textContent=`
/* Ensure native cursor visibility across the entire hero */
.agro-hero,
.agro-hero * {
  cursor: auto;
}
.agro-hero a,
.agro-hero button,
.agro-hero [role="button"],
.agro-hero a * {
  cursor: pointer !important;
}

@keyframes kc-seed-drop {
  0% {
    transform: translate3d(0, 0, 0) rotate(0deg) scale(0.9);
    opacity: 1;
  }
  65% {
    transform: translate3d(var(--kc-drift-x), calc(var(--kc-fall-y) * 0.8), 0) rotate(var(--kc-rot)) scale(0.8);
    opacity: 0.95;
  }
  100% {
    transform: translate3d(var(--kc-drift-x), var(--kc-fall-y), 0) rotate(var(--kc-rot)) scale(0.65);
    opacity: 0;
  }
}

@keyframes kc-plant-sprout {
  0% {
    transform: translate3d(-50%, 0, 0) scaleY(0) scaleX(0.4);
    opacity: 0;
  }
  50% {
    transform: translate3d(-50%, -6px, 0) scaleY(1.15) scaleX(1.08);
    opacity: 1;
  }
  75% {
    transform: translate3d(-50%, 2px, 0) scaleY(0.96) scaleX(0.98);
    opacity: 1;
  }
  100% {
    transform: translate3d(-50%, 0, 0) scaleY(1) scaleX(1);
    opacity: 1;
  }
}

@keyframes kc-plant-sway {
  0%, 100% {
    transform: translate3d(-50%, 0, 0) rotate(-4deg);
  }
  50% {
    transform: translate3d(-50%, 0, 0) rotate(4deg);
  }
}

@keyframes kc-fade-out {
  0% {
    opacity: 1;
    transform: translate3d(-50%, 0, 0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translate3d(-50%, -4px, 0) scale(0.85);
  }
}

.kc-seed {
  position: fixed;
  pointer-events: none !important;
  user-select: none !important;
  z-index: 99999;
  font-size: var(--kc-size);
  line-height: 1;
  will-change: transform, opacity;
  animation: kc-seed-drop var(--kc-dur) cubic-bezier(0.38, 0, 0.7, 1) forwards;
}

.kc-plant {
  position: fixed;
  pointer-events: none !important;
  user-select: none !important;
  z-index: 99998;
  font-size: var(--kc-size);
  line-height: 1;
  transform-origin: center bottom;
  opacity: 0;
  will-change: transform, opacity;
}

.kc-plant.is-growing {
  animation:
    kc-plant-sprout var(--kc-grow-dur) cubic-bezier(0.34, 1.56, 0.64, 1) forwards,
    kc-plant-sway 2.2s ease-in-out var(--kc-grow-dur) infinite;
}

.kc-plant.is-fading {
  animation: kc-fade-out var(--kc-fade-dur) ease-out forwards !important;
}

.kc-soil-patch {
  position: fixed;
  pointer-events: none !important;
  user-select: none !important;
  z-index: 99997;
  width: var(--kc-soil-w);
  height: 6px;
  border-radius: 50%;
  background: radial-gradient(ellipse at center, rgba(16, 185, 129, 0.5) 0%, rgba(5, 150, 105, 0.25) 50%, transparent 80%);
  transform: translate3d(-50%, 0, 0);
  opacity: 0;
  will-change: opacity;
}

.kc-soil-patch.is-growing {
  opacity: 0.9;
  transition: opacity 0.35s ease-out;
}

.kc-soil-patch.is-fading {
  opacity: 0;
  transition: opacity var(--kc-fade-dur) ease-out;
}
`,document.head.appendChild(e)}function p(){let e=(0,n.useRef)(0),t=(0,n.useRef)(!0);return(0,n.useEffect)(()=>{t.current=!0,f();let n=(n,d,f)=>{let p=performance.now();if(p-e.current<r)return;e.current=p;let m=Math.round(u(18,25)),h=Math.round(u(24,32)),g=h*1.8,_=n,v=d+18,y=u(75,130),b=Math.min(f-h-8,window.innerHeight-h-8),x=Math.min(b,v+y),S=Math.max(35,x-v),C=u(-14,14),w=u(-22,22),T=document.createElement(`div`);T.className=`kc-seed`,T.textContent=c[Math.floor(Math.random()*c.length)],T.style.cssText=[`left:${_}px`,`top:${v}px`,`--kc-size:${m}px`,`--kc-fall-y:${S}px`,`--kc-drift-x:${C}px`,`--kc-rot:${w}deg`,`--kc-dur:${i}ms`].join(`;`),document.body.appendChild(T),setTimeout(()=>{if(!t.current){T.remove();return}T.remove();let e=_+C,n=x,r=document.createElement(`div`);r.className=`kc-soil-patch`,r.style.cssText=[`left:${e}px`,`top:${n+6}px`,`--kc-soil-w:${g}px`,`--kc-fade-dur:${s}ms`].join(`;`),document.body.appendChild(r),r.offsetWidth,r.classList.add(`is-growing`);let i=document.createElement(`div`);i.className=`kc-plant`,i.textContent=l[Math.floor(Math.random()*l.length)],i.style.cssText=[`left:${e}px`,`top:${n-h+6}px`,`--kc-size:${h}px`,`--kc-grow-dur:${a}ms`,`--kc-fade-dur:${s}ms`].join(`;`),document.body.appendChild(i),i.offsetWidth,i.classList.add(`is-growing`),setTimeout(()=>{t.current?(i.classList.remove(`is-growing`),i.classList.add(`is-fading`),r.classList.remove(`is-growing`),r.classList.add(`is-fading`),setTimeout(()=>{i.remove(),r.remove()},650)):(i.remove(),r.remove())},o)},i)},d=e=>{let t=document.querySelector(`.agro-hero`);if(!t)return;let r=t.getBoundingClientRect();e.clientY>=0&&e.clientY<=r.bottom&&e.clientX>=r.left&&e.clientX<=r.right&&r.bottom>80&&n(e.clientX,e.clientY,r.bottom)};return window.addEventListener(`mousemove`,d,{passive:!0}),()=>{t.current=!1,window.removeEventListener(`mousemove`,d),document.querySelectorAll(`.kc-seed, .kc-plant, .kc-soil-patch`).forEach(e=>e.remove())}},[]),null}export{p as default};