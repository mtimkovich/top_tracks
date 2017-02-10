var sounds = document.getElementsByTagName('audio');

for (let sound of sounds) {
    let next_num = +sound.id.match(/\d+/)[0]+1;
    let next = document.getElementById('audio-' + next_num);

    if (next) {
        sound.addEventListener('ended', () => {
            sound.currentTime = 0;
            next.play();
        });
    }
}
