function likeLocation(locationName) {
    // 发送点赞请求到后端
    fetch('/like_location', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'location': locationName }),
    })
    .then(response => response.json())
    .then(data => {
        alert("点赞成功！");
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function rateLocation(locationName, rating) {
    // 发送评分请求到后端
    fetch('/rate_location', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'location': locationName, 'rating': rating }),
    })
    .then(response => response.json())
    .then(data => {
        alert("评分成功！");
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
