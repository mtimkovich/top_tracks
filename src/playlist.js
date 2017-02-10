var sounds = document.getElementsByTagName('iframe');

for (let i = 0; i < sounds.length-1; i++) {
    let sound = sounds[i];
    let curr = SC.Widget(sound.id);
    let next_num = +sound.id.match(/\d+/)[0]+1;
    let next = SC.Widget('audio-' + next_num);

    curr.bind(SC.Widget.Events.FINISH, () => {
        next.play();
    });
}
