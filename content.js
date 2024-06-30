(async () => {
    const search = new URLSearchParams(window.location.search);
    if(search.has("post")) {
        const index = parseInt(search.get("post"));
        // Fetch database.json
        let res = await fetch("/assets/database.json");
        if (!res.ok) throw new Error(`Error fetching database.json: ${res.statusText}`);
        const data = await res.json();

        // Fetch the content file
        if(data.posts[index]) {
            const contentFilename = data.posts[index].content_filename;
            res = await fetch(`/assets/posts/${contentFilename}`); 
            if (!res.ok) {
                console.log(res.statusText);
                throw new Error(`Error fetching ${contentFilename}: ${res.statusText}`);
            }
            const content = await res.text();

            // Update the content of the element with id 'content'
            const contentElement = document.getElementById("content");
            if (contentElement) {
                contentElement.innerHTML = md2html(content);
            } else {
                throw new Error("Element with id 'content' not found.");
            }
        } else {

        }
    } else {
    }
})();
