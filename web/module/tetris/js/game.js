var Game = function()
{
	var gameDiv; 
	var nextDiv ;
	var timeDiv ;
	var scoreDiv ;
	var score = 0 ;
	var gameData = [
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0]
	];

	// current square
	var cur ; 
	// next square	
	var next ;
	var nextDivs = [];
	var gameDivs = [];


	var initDiv = function(container,data,divs){
		for(var i = 0 ; i < data.length ; i++)
		{
			var div = [];
			for(var j = 0 ; j < data[0].length ; j++)
			{
				var newNode = document.createElement("div");
				newNode.className = "none";
				newNode.style.top = (i*20) + "px";
				newNode.style.left = (j*20) + "px";
				container.appendChild(newNode);
				div.push(newNode);
			}
			divs.push(div);
		}
	}


	var refashDiv = function(data,divs){
		for(var i = 0 ; i < data.length ; i++)
		{
			for(var j = 0 ; j < data[0].length ; j++)
			{
				if(data[i][j] === 0)
				{
					divs[i][j].className = "none";
				}
				else if(data[i][j] === 1)
				{
					divs[i][j].className = "done";
				}
				else if(data[i][j] === 2)
				{
					divs[i][j].className = "current";
				}
			}
		}
	}

	var isValid = function(pos,data)
	{
		for(var i = 0 ; i < data.length ; i++)
		{
			for(var j = 0 ; j < data[0].length; j++)
			{
				if(data[i][j] !== 0)
				{
					if(!check(pos,i,j))
					 {
					 	return false ;
					 }
				}
			}
		}

		return true ;
	}
	// check dot is right
	var check = function(pos,x,y)
	{
		if(pos.x + x < 0)
		{
			return false ;
		}
		else if(pos.x + x >= gameData.length)
		{
			return false ;
		}
		else if(pos.y + y < 0)
		{
			return false ;
		}
		else if(pos.y + y >= gameData[0].length)
		{
			return false ;
		}
		else if(gameData[pos.x + x][pos.y + y] === 1)
		{
			return false ;
		}
		else 
		{
			return true ;
		}
	}
	var cleanData = function()
	{
		for(var i = 0 ; i < cur.data.length ; i++)
		{
			for(var j = 0 ; j < cur.data[0].length; j++)
			{
				if(check(cur.origin,i,j))
					gameData[cur.origin.x + i ][cur.origin.y + j] = 0; 
			}
		}
	}
	var setData = function()
	{
		for(var i = 0 ; i < cur.data.length ; i++)
		{
			for(var j = 0 ; j < cur.data[0].length; j++)
			{
				if(check(cur.origin,i,j))
					gameData[cur.origin.x + i ][cur.origin.y + j] = cur.data[i][j]; 
			}
		}
	}

	var rotate = function()
	{
		if(cur.canRotate(isValid))
		{
			cleanData();
			//cur.origin.x = cur.origin.x + 1 ;
			cur.rotate();
			setData();
			refashDiv(gameData,gameDivs);

		}
	}
	var down = function()
	{
		if(cur.canDown(isValid))
		{
			cleanData();
			//cur.origin.x = cur.origin.x + 1 ;
			cur.down();
			setData();
			refashDiv(gameData,gameDivs);
			return true ;
		}
		else
		{
			return false ;
		}
	}

	// down to end 
	var fall = function()
	{
		while(down())
		{
			;
		}
	}

	var left = function()
	{
		if(cur.canLeft(isValid))
		{
			cleanData();
			//cur.origin.x = cur.origin.x + 1 ;
			cur.left();
			setData();
			refashDiv(gameData,gameDivs);

		}
	}


	var right = function()
	{
		if(cur.canRight(isValid))
		{
			cleanData();
			//cur.origin.x = cur.origin.x + 1 ;
			cur.right();
			setData();
			refashDiv(gameData,gameDivs);

		}
	}


	var fixed = function()
	{
		for(var i = 0 ; i < cur.data.length ; i++)
		{
			for(var j = 0 ; j < cur.data[0].length; j++)
			{
				if(check(cur.origin, i , j))
				{
					if(gameData[cur.origin.x + i][cur.origin.y+j] === 2)
					{
						gameData[cur.origin.x + i][cur.origin.y+j] = 1 ;
					}
				}
			}
		}
		refashDiv(gameData,gameDivs)
	}

	var preformNext = function(type,dir)
	{
		cur = next ;
		setData();
		next = SquareFactory.prototype.make(type,dir);
		refashDiv(gameData,gameDivs);
		refashDiv(next.data,nextDivs);
	}

	var checkClear = function(){
		var clearLine = 0 ;
		for(var i = gameData.length-1; i>=0 ; i--)
		{
			var clear = true ; 
			for(var j = 0 ;j < gameData[0].length ; j++)
			{
				if(gameData[i][j] !== 1){
					clear = false ; 
					break ; 
				}
			}
			if(clear)
			{
				clearLine = clearLine + 1 ;
				for(var m = i ; m > 0 ; m--)
				{
					for(var n = 0 ; n < gameData[0].length; n++)
					{
						gameData[m][n] = gameData[m-1][n];
					}
				}

				for(var n = 0;  n < gameData[0].length ; n++)
				{
					gameData[0][n] = 0 ;
				}
				i++ ;
			}
		}
		return clearLine ;
	}

	var checkGameOver = function()
	{
		var gameOver = false ;
		for(var i = 0 ; i < gameData[0].length ; i++)
		{
			if(gameData[1][i] === 1)
			{
				gameOver = true;
			}
		}

		return gameOver ;
	}	

	var setTime = function(time)
	{
		timeDiv.innerHTML = time ;
	}

	var addSocre = function(line)
	{
		var s = 0 ;
		switch(line)
		{
			case 1:
				s = 10 ; 
				break;
			case 2:
				s = 30 ;
				break; 
			case 3:
				s = 60 ;
				break; 
			case 4:
				s = 100;
				break;
			default:
				break;
		}

		score = score + s ; 
		scoreDiv.innerHTML = score ;
	}
	var gameOver = function(win)
	{
        window.parent.$.ajax({
            type: 'POST',
            url: localStorage.getItem('server') + '/games/set/score',
            data: JSON.stringify({type: 'tetris', score: score}),
            contentType: 'application/json',
            success: function (data) {
                if (data.code === 0) {
                    let r = window.parent.i18next.t("game.result.lost");
                    if(win) {
                        r = window.parent.i18next.t("game.result.win");
                    }
                    reloadGame(score, r);
                } else {
                    window.parent.$.Toast(data.msg, 'error');
                }
            }
        })
	}

	// 增加干扰项目，底部增加行
	var addTailLines = function(lines)
	{
		for(var i = 0 ;i < gameData.length - lines.length ; i++)
		{
			gameData[i] = gameData[i + lines.length];
		}

		for(var i = 0 ; i < lines.length; i++)
		{
			gameData[gameData.length - lines.length + i] = lines[i];
		}
		cur.origin.x = cur.origin.x - lines.length ;
		if(cur.origin.x < 0)
		{
			cur.origin.x = 0 ;
		}

		refashDiv(gameData,gameDivs);
	}

	var init = function(doms,type,dir)
	{
		gameDiv = doms.gameDiv; 
		nextDiv = doms.nextDiv;
		timeDiv = doms.timeDiv;
		scoreDiv = doms.scoreDiv;
		let i18nList = document.getElementsByClassName('i18n');
		for (let i=0; i<i18nList.length; i++) {i18nList[i].innerText = window.parent.i18next.t(i18nList[i].getAttribute('key'));}
		window.parent.document.querySelectorAll('.window.game>.titbar>span>.title')[0].innerText = window.parent.i18next.t('game.tetris');
		next = SquareFactory.prototype.make(type,dir);
		initDiv(gameDiv,gameData,gameDivs);
		initDiv(nextDiv,next.data,nextDivs);	
		refashDiv(next.data,nextDivs);
		reloadScoreList();
	}

    var reloadGame = function (score,overReason) {
        var text = window.parent.i18next.t('game.snake.result.text1');
        var text2 = window.parent.i18next.t('game.snake.result.text2');
        document.getElementsByClassName('wrapper')[0].style.display = 'flex';
        document.getElementsByClassName('box-header')[0].innerHTML = overReason;
        document.getElementsByClassName('box-content')[0].innerHTML = text + score + text2;
        document.getElementsByClassName('skip')[0].onclick = function () {
            window.location.reload();
        };
    };

	var reloadScoreList = function(){
		window.parent.$.ajax({
			type: 'GET',
			url: localStorage.getItem('server') + '/games/get/rank/tetris',
			success: function (data) {
				if (data.code === 0) {
					let scoreList = data.data;
					let rankString = '';
					for(let i=0; i<scoreList.length; i++){
						rankString += '<p><span class="user-name">' + scoreList[i].name + '</span>:<span class="score-num">' + scoreList[i].score + '</span></p>';
					}
					document.getElementsByClassName('ranking')[0].innerHTML = rankString;
				} else {
					window.parent.$.Toast(data['msg'], 'error');
				}
			}
		})
	}

	// report fun
	this.init = init;
	this.down = down;
	this.right = right;
	this.left = left ;
	this.rotate = rotate ;
	this.fall = fall ;
	this.fixed = fixed ;
	this.preformNext = preformNext ;
	this.checkClear = checkClear;
	this.checkGameOver = checkGameOver ;  
	this.setTime = setTime ; 
	this.addSocre = addSocre ;
	this.gameOver = gameOver ;
	this.addTailLines = addTailLines ;
}