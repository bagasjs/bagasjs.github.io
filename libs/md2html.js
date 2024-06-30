const TAILWIND_LIGHTONLY_CONFIG = {
    "h1": { "class": "text-6xl mb-3 pb-3 border-b border-black" },
    "h2": { "class": "text-5xl mb-3 pb-3 border-b border-black" },
    "h3": { "class": "text-4xl mb-3 pb-3 border-b border-black" },
    "h4": { "class": "text-3xl mb-3 pb-3 border-b border-black" },
    "h5": { "class": "text-2xl mb-3 pb-3 border-b border-black" },
    "h6": { "class": "text-xl  mb-3 pb-3 border-b border-black" },
    "a": { "class": "text-blue-500" },
    "p": { "class": "text-black mb-3" },
    "blockquote": { "class": "italic mb-3 text-gray-700 border-l-4 border-gray-400 pl-4 py-2 mb-3" },
}
const TAILWIND_CONFIG = {
    "h1": { "class": "text-6xl mb-3 pb-3 border-b border-black dark:text-white dark:border-white" },
    "h2": { "class": "text-5xl mb-3 pb-3 border-b border-black dark:text-white dark:border-white" },
    "h3": { "class": "text-4xl mb-3 pb-3 border-b border-black dark:text-white dark:border-white" },
    "h4": { "class": "text-3xl mb-3 pb-3 border-b border-black dark:text-white dark:border-white" },
    "h5": { "class": "text-2xl mb-3 pb-3 border-b border-black dark:text-white dark:border-white" },
    "h6": { "class": "text-xl mb-3 pb-3 border-b border-black" },
    "a": { "class": "text-blue-500" },
    "p": { "class": "text-black dark:text-white" },
    "blockquote": { "class": "italic text-gray-700 border-l-4 border-gray-400 pl-4 py-2 mb-3" },
    "code": { "class": "text-gray-900 bg-gray-200 px-2 py-1" },
}

function escapeHtml(unsafe)
{
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
 }

/**
 * A simple implementation of Markdown to HTML compiler
 * Features: headers, bold, italics, links, images
 * @param {string} source
 * @param {MD2HTMLConfig} config
 * @returns {string}
 */
function md2html(source, config) {
    if (!config) config = TAILWIND_LIGHTONLY_CONFIG;

    function attrsOf(element) {
        if (!config || !config[element]) return "";
        const attrs = config[element];
        return Object.entries(attrs).map(([key, value]) => `${key}="${value}"`).join(" ");
    }

    /**
     * @param {string} inner 
     * @returns {string}
     */
    function compileInner(inner) {
        // Handle bold, italics, links, and images using regex
        inner = inner.replace(/!\[(.*?)\]\((.*?)\)/g, '<img src="$2" alt="$1">');
        inner = inner.replace(/\[(.*?)\]\((.*?)\)/g, '<a ' + attrsOf("a") +  ' href="$2">$1</a>');
        inner = inner.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'); // Matches **text**
        inner = inner.replace(/\*(.*?)\*/g, '<em>$1</em>'); // Matches *text*
        return inner;
    }

    /**
     * @param {string} line
     * @returns {string}
     */
    function compileLine(line) {
        if (line.startsWith("#")) {
            let level = 0;
            for (level = 0; level < line.length && line[level] == "#"; level++);
            level = Math.min(level, 6);
            const inner = compileInner(line.slice(level).trim());
            const element = `h${level}`;
            return `<${element} ${attrsOf(element)}>${inner}</${element}>`;
        } else if (line.startsWith(">")) {
            const inner = compileInner(line.slice(1).trim());
            const element = "blockquote";
            return `<${element} ${attrsOf(element)}>${inner}</${element}>`;
        } else {
            const element = "p";
            return `<${element} ${attrsOf(element)}>${compileInner(line)}</${element}>`;
        }
    }

    const lines = source.split("\n");
    const compiled = [];

    for(const line of lines.filter(line => line.trim().length !== 0)) {
        compiled.push(compileLine(line));
    }

    return compiled.join("\n");
}

