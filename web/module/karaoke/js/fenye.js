/**
 * 对页面进行分页
 * @param obj 页码标签对象
 * @param  pageNum 分页总数
 * @param currentpage number 当前页
 * @param prePage
 * @param nextPage
 */

function PagingManage(obj, pageNum, currentpage, prePage="上一页", nextPage="下一页") {
    if (obj) {
        let showPageNum = 7;//显示多少个页码
        let pagehtml = "";

        //只有一页内容
        if (pageNum <= 1) {
            pagehtml = "";
        }

        //大于一页内容
        if (pageNum > 1) {
            if (currentpage > 1) {
                pagehtml += '<li><a href="#" onclick="get_song_list(' + (currentpage - 1) + ')">' + prePage +'</a></li>';
            }

            //计算页码开始位置
            if (showPageNum >= pageNum) {//如果要显示的页码大于总的页码数
                for (let i = 1; i <= showPageNum; i++) {
                //如果要输出的页面大于总的页面数,则退出
                if (i > pageNum) {
                    break;
                }
                if (i === currentpage) {
                    pagehtml += '<li><a class="active" href="#" onclick="get_song_list(' + i + ')">' + i + '</a></li>';
                } else {
                    pagehtml += '<li><a href="#" onclick="get_song_list(' + i + ')">' + i + '</a></li>';
                }
            }
            } else {//如果要显示的页码小于总的页码数
                if (currentpage < 4) {
                    for (let i = 1; i <= 5; i++) {
                        if (i === currentpage) {
                            pagehtml += '<li><a class="active" href="#" onclick="get_song_list(' + i + ')">' + i + '</a></li>';
                        } else {
                            pagehtml += '<li><a href="#" onclick="get_song_list(' + i + ')">' + i + '</a></li>';
                        }
                    }
                    pagehtml += '<li><a>...</a></li>';
                    pagehtml += '<li><a href="#" onclick="get_song_list(' + pageNum + ')">' + pageNum + '</a></li>';
                } else if (currentpage > pageNum-3) {
                    pagehtml += '<li><a href="#" onclick="get_song_list(' + 1 + ')">' + 1 + '</a></li>';
                    pagehtml += '<li><a>...</a></li>';
                    for (let i = pageNum-4; i <= pageNum; i++) {
                        if (i === currentpage) {
                            pagehtml += '<li><a class="active" href="#" onclick="get_song_list(' + i + ')">' + i + '</a></li>';
                        } else {
                            pagehtml += '<li><a href="#" onclick="get_song_list(' + i + ')">' + i + '</a></li>';
                        }
                    }
                } else {
                    pagehtml += '<li><a href="#" onclick="get_song_list(' + 1 + ')">' + 1 + '</a></li>';
                    pagehtml += '<li><a>...</a></li>';
                    for (let i = currentpage-1; i <= currentpage+1; i++) {
                        if (i === currentpage) {
                            pagehtml += '<li><a class="active" href="#" onclick="get_song_list(' + i + ')">' + i + '</a></li>';
                        } else {
                            pagehtml += '<li><a href="#" onclick="get_song_list(' + i + ')">' + i + '</a></li>';
                        }
                    }
                    pagehtml += '<li><a>...</a></li>';
                    pagehtml += '<li><a href="#" onclick="get_song_list(' + pageNum + ')">' + pageNum + '</a></li>';
                }
            }
            if (currentpage < pageNum) {
                pagehtml += '<li><a href="#" onclick="get_song_list(' + (currentpage + 1) + ')">' + nextPage +'</a></li>';
            }
        }
        obj.innerHTML = pagehtml;
    }
}
