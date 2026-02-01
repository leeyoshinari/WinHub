function MessageBox() {}
MessageBox.prototype.reloadScoreList = function(callback){
    window.parent.$.ajax({
        type: 'GET',
        url: localStorage.getItem('server') + '/games/get/rank/snake',
        success: function (data) {
            if (data.code === 0) {
                let scoreList = data.data;
                let rankString = '';
                for(let i=0; i<scoreList.length; i++){
                    rankString += '<p><span class="user-name">' + scoreList[i].username + '</span>:<span class="score-num">' + scoreList[i].score + '</span></p>';
                }
                document.getElementsByClassName('ranking')[0].innerHTML = rankString;
                document.getElementsByClassName('score name')[0].innerText = data.msg;
            } else {
                window.parent.$.Toast(data['msg'], 'error');
            }
        }
    })
}

// 游戏结束后的弹框
MessageBox.prototype.reloadGame = function (score,overReason) {
  var text = window.parent.i18next.t('game.snake.result.text1');
  var text2 = window.parent.i18next.t('game.snake.result.text2');
  // 显示弹框，隐藏掉输入框，修改掉部分文本
  document.getElementsByClassName('wrapper')[0].style.display = 'flex';
  document.getElementsByClassName('box-header')[0].innerHTML = overReason;
  document.getElementsByClassName('box-content')[0].innerHTML = text + score + text2;
  document.getElementsByClassName('skip')[0].innerHTML = window.parent.i18next.t('game.snake.restart');
  document.getElementsByClassName('head-button')[0].style.display = 'none';
  document.getElementsByClassName('skip')[0].onclick = function () {
    window.location.reload();
  };
};

let messageBox = new MessageBox();
// 游戏结束后的处理逻辑
let OverDeal = function (gameData) {
    let para = JSON.stringify({
        type: 'snake',
        score: gameData.score - 1
    });

    // messageBox.reloadGame(gameData.score - 1,gameData.overReason);
    window.parent.$.ajax({
        type: 'POST',
        url: localStorage.getItem('server') + '/games/set/score',
        data: para,
        contentType: 'application/json',
        success: function (data) {
            if (data.code === 0) {
                messageBox.reloadScoreList();
                messageBox.reloadGame(gameData.score - 1,gameData.overReason);
            } else {
                window.parent.$.Toast(data.msg, 'error');
            }
        }
    })
};

let snakeObject = new Snake({
    gameSpeed: 500,
    gameOver: OverDeal
});

init();

function init(){
    snakeObject.drawChessBoard();// 画棋盘
    window.parent.document.querySelectorAll('.window.game>.titbar>span>.title')[0].innerText = window.parent.i18next.t('game.snake');
    let i18nList = document.getElementsByClassName('i18n');
    for (let i=0; i<i18nList.length; i++) {i18nList[i].innerText = window.parent.i18next.t(i18nList[i].getAttribute('key'));}
    messageBox.reloadScoreList(); // 渲染榜单记录
    snakeObject.upDownAnimation(function () {   // 欢迎动画
        // 开始游戏
        snakeObject.beginGame();
        snakeObject.listenKeyDown(); //监听上下左右按钮
        let firstBody = snakeObject.createRandomBlock('black',true);// 创建蛇身
        snakeObject.headerTr = firstBody.horizon;// 初始化蛇头位置
        snakeObject.headertd = firstBody.vertical;
        snakeObject.snakeBody.push(snakeObject.tds[snakeObject.headerTr][snakeObject.headertd]);//将蛇头放入蛇身
        snakeObject.createEgg(true);// 创建一个蛋
    });
    document.getElementById('left').addEventListener('click', () => {snakeObject.turn('left');})
    document.getElementById('right').addEventListener('click', () => {snakeObject.turn('right');})
    document.getElementById('up').addEventListener('click', () => {snakeObject.turn('up');})
    document.getElementById('down').addEventListener('click', () => {snakeObject.turn('down');})
}
