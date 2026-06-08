import MarkdownIt from "markdown-it";
import hljs from "highlight.js";
import mila from "markdown-it-link-attributes";
import renderMathInElement from "katex/dist/contrib/auto-render.mjs";
// @ts-ignore
import katex from "katex";

export default defineNuxtPlugin(() => {
  const renderer = MarkdownIt({
    html: true,
    breaks: true,
    linkify: true,
    highlight(code, language) {
      const validLang = !!(language && hljs.getLanguage(language));
      if (validLang) {
        const lang = language ?? "";
        return highlightBlock(
          hljs.highlight(code, { language: lang }).value,
          lang
        );
      }
      return highlightBlock(hljs.highlightAuto(code).value, "");
    },
  });
  renderer.use(mila, { attrs: { target: "_blank", rel: "noopener" } });

  const highlightBlock = (str, lang) => {
    return `<pre class="code-block-wrapper"><div class="code-block-header"><span class="code-block-header__lang">${lang}</span><span class="code-block-header__copy">Copy</span></div><code class="hljs code-block-body ${lang}">${str}</code></pre>`;
  };

  const processLatex = (text) => {
    // 处理块级公式
    text = text.replace(/\\\[(.+?)\\\]/g, (match, latex) => {
      let latexContent = latex.trim();
      // 移除 ', \\tag{数字}' 这样的序号标签
      latexContent = latexContent.replace(/,?\s*\\tag{\d+}/, "");
      return `<div class="katex-block">${katex.renderToString(latexContent, {
        displayMode: true,
        strict: false,
      })}</div>`;
    });

    // 处理内联公式
    text = text.replace(/\\\((.+?)\\\)/g, (match, latex) => {
      return katex.renderToString(latex, { displayMode: false, strict: false });
    });

    return text;
  };

  const renderWithFootnotes = (text, index) => {
    let processedText = text;
    try {
      processedText = processLatex(processedText);

      processedText = processedText.replace(/\[(\d+)\]/g, (match, p1) => {
        return `<sup class="footnote-ref cursor-pointer text-blue-500" data-id="${index}-${p1}">[${p1}]</sup>`;
      });

      // 渲染 Markdown
      let rendered = renderer.render(processedText);

      // 创建一个临时的 DOM 元素来应用 KaTeX 自动渲染
      const tempElement = document.createElement("div");
      tempElement.innerHTML = rendered;

      // 应用 KaTeX 自动渲染
      renderMathInElement(tempElement, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "$", right: "$", display: false },
          { left: "\\(", right: "\\)", display: false },
          { left: "\\[", right: "\\]", display: true },
        ],
        throwOnError: false,
      });

      // 返回处理后的 HTML
      return tempElement.innerHTML;
    } catch (error) {
      console.error("Error rendering markdown:", error);
      return text; // 在出错时返回原始文本
    }
  };

  return {
    provide: {
      mdRenderer: {
        render: renderWithFootnotes,
      },
    },
  };
});
