(() => {
    'use strict'

    const waveContainer = document.getElementById("wave");
    const barsCount = (waveContainer.parentElement.clientWidth / 10);

    for (let i=0; i < barsCount; i++) {
        const waveSampleEl = document.createElement("div");

        waveSampleEl.classList.add("waveform-bar");
        waveContainer.appendChild(waveSampleEl);
    }

    anime({
        targets: '.waveform-bar',
        easing: 'easeInOutQuad',
        duration: 400,
        height: [4, () => anime.random(8, 100)],
        opacity: anime.stagger([2, 0.3], {from: 'center', easing: 'easeOutQuad' }),
        delay: anime.stagger(10, { from: 'center', easing: 'easeOutQuad' })
    });
})()