(async () => {
    const url = "https://raw.githubusercontent.com/bagasjs/bagasjs.github.io/main/assets/database.json"
    const res = await fetch(url);
    const data = await res.json();
    let content = "";
    for(const [index, post] of Object.entries(data.posts)) {
        const createdAt = new Date(post.created_at);
        const thumnail = post.thumbnail ? post.thumnail : "/assets/icons/na.png";
        content += `
            <a href="/content.html?post=${index}" class="flex flex-col items-center">
                <img class="" width="300" height="300" src="${thumnail}"/>
                <div>
                    <h3 class="text-3xl font-bold">${post.title}</h3>
                    <p class="text-xs font-light">${createdAt}</p>
                    <p>${post.excerpt}</p>
                </div>
            </a>
        `;
    }

    document.getElementById("posts-list").innerHTML = content;
})();
