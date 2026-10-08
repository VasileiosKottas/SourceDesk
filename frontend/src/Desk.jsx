import { useEffect, useState } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";
import {
  askQuestion,
  createLink,
  getFile,
  getFilePages,
  getFiles,
  getLink,
  getLinks,
  getQuestions,
  logout,
  uploadFile,
} from "./api";

const MATH = /\\\[([\s\S]+?)\\\]|\\\(([\s\S]+?)\\\)/g;

function visibleAnswer(text) {
  return text.replace(/\n*Sources used:[\s\S]*$/i, "").trimEnd();
}

function answerParts(text) {
  const parts = [];
  let last = 0;
  for (const match of text.matchAll(MATH)) {
    if (match.index > last) {
      parts.push({ text: text.slice(last, match.index) });
    }
    parts.push({
      tex: match[1] !== undefined ? match[1] : match[2],
      display: match[1] !== undefined,
    });
    last = match.index + match[0].length;
  }
  if (last < text.length) {
    parts.push({ text: text.slice(last) });
  }
  return parts;
}

function AnswerText({ text }) {
  const parts = answerParts(visibleAnswer(text));
  return (
    <div className="answer">
      {parts.map((part, index) => {
        if (part.tex === undefined) {
          return (
            <span key={index} className="answer-text">
              {part.text}
            </span>
          );
        }
        const html = katex.renderToString(part.tex, {
          throwOnError: false,
          displayMode: part.display,
        });
        const Tag = part.display ? "div" : "span";
        return (
          <Tag
            key={index}
            className={part.display ? "math-display" : "math-inline"}
            dangerouslySetInnerHTML={{ __html: html }}
          />
        );
      })}
    </div>
  );
}

export default function Desk({ user, onLogout }) {
  const [links, setLinks] = useState([]);
  const [files, setFiles] = useState([]);
  const [url, setUrl] = useState("");
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [history, setHistory] = useState([]);
  const [currentId, setCurrentId] = useState(null);
  const [openId, setOpenId] = useState(null);
  const [asking, setAsking] = useState(false);
  const [pageCount, setPageCount] = useState(0);

  async function load() {
    const [linkData, fileData, questionData] = await Promise.all([
      getLinks(),
      getFiles(),
      getQuestions(),
    ]);
    setLinks(linkData.links);
    setFiles(fileData.files);
    setHistory(questionData.questions);
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function handleLink(event) {
    event.preventDefault();
    setError("");
    try {
      await createLink(url, title, notes);
      setUrl("");
      setTitle("");
      setNotes("");
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleFile(event) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }
    setError("");
    try {
      await uploadFile(file);
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleLogout() {
    await logout();
    onLogout();
  }

  async function handleQuestion(event) {
    event.preventDefault();
    setError("");
    setAsking(true);
    try {
      const data = await askQuestion(question);
      setAnswer(data.answer);
      setSources(data.sources || []);
      setCurrentId(data.question?.id ?? null);
      setOpenId(null);
      setQuestion("");
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setAsking(false);
    }
  }

  async function openItem(kind, id) {
    setError("");
    setPageCount(0);
    try {
      const data = kind === "file" ? await getFile(id) : await getLink(id);
      const item = data.file || data.link;
      setSelected({ kind, item });
      if (kind === "file" && item.file_name?.toLowerCase().endsWith(".pdf")) {
        const pages = await getFilePages(item.id);
        setPageCount(pages.count);
      }
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="desk">
      <header>
        <div>
          <p className="eyebrow">SourceDesk</p>
          <h1>{user.name}'s desk</h1>
        </div>
        <button type="button" onClick={handleLogout}>
          Log out
        </button>
      </header>
      {error && <p className="error">{error}</p>}
      <section className="panel">
        <h2>Ask</h2>
        <form onSubmit={handleQuestion} className="stack">
          <input
            placeholder="Ask about your files and links"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            required
          />
          <button type="submit" className="ask-button" disabled={asking} aria-busy={asking}>
            {asking ? <span className="spinner" aria-label="Asking" /> : "Ask"}
          </button>
        </form>
        {answer && <AnswerText text={answer} />}
        {sources.length > 0 && (
          <ul>
            {sources.map((source) => {
              const isFile = Boolean(source.file_name);
              const label = isFile ? `file: ${source.file_name}` : `link: ${source.title}`;
              return (
                <li key={`${isFile ? "file" : "link"}-${source.id}`}>
                  <button
                    type="button"
                    className="item-button"
                    onClick={() => openItem(isFile ? "file" : "link", source.id)}
                  >
                    {label}
                  </button>
                </li>
              );
            })}
          </ul>
        )}
        {history.some((item) => item.id !== currentId) && (
          <ul>
            {history
              .filter((item) => item.id !== currentId)
              .map((item) => (
                <li key={item.id}>
                  <button
                    type="button"
                    className="item-button"
                    aria-expanded={openId === item.id}
                    onClick={() => setOpenId(openId === item.id ? null : item.id)}
                  >
                    {item.question}
                  </button>
                  {openId === item.id && (
                    <>
                      {item.answer && <AnswerText text={item.answer} />}
                      {(item.labels || []).map((label) => (
                        <button
                          key={`${item.id}-${label.kind}-${label.id}`}
                          type="button"
                          className="item-button"
                          onClick={() => openItem(label.kind, label.id)}
                        >
                          {label.label}
                        </button>
                      ))}
                    </>
                  )}
                </li>
              ))}
          </ul>
        )}
      </section>
      <section className="panel">
        <h2>Links</h2>
        <form onSubmit={handleLink} className="stack">
          <input
            placeholder="https://example.com"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            required
          />
          <input
            placeholder="Title"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            required
          />
          <input
            placeholder="Notes"
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
          />
          <button type="submit">Save link</button>
        </form>
        {links.length === 0 ? (
          <p className="muted">No links yet.</p>
        ) : (
          <ul>
            {links.map((link) => (
              <li key={link.id}>
                <button type="button" className="item-button" onClick={() => openItem("link", link.id)}>
                  {link.title}
                </button>
                {link.notes && <span>{link.notes}</span>}
                {link.content_error && <span className="error">{link.content_error}</span>}
              </li>
            ))}
          </ul>
        )}
      </section>
      <section className="panel">
        <h2>Files</h2>
        <label className="file-picker">
          Upload a file
          <input type="file" onChange={handleFile} />
        </label>
        {files.length === 0 ? (
          <p className="muted">No files yet.</p>
        ) : (
          <ul>
            {files.map((file) => (
              <li key={file.id}>
                <button type="button" className="item-button" onClick={() => openItem("file", file.id)}>
                  {file.file_name}
                </button>
                <span>
                  {file.file_type} · {file.file_size} bytes
                </span>
                {file.content_error && <span className="error">{file.content_error}</span>}
              </li>
            ))}
          </ul>
        )}
      </section>
      {selected && (
        <section className="panel">
          <h2>{selected.item.file_name || selected.item.title}</h2>
          {selected.kind === "link" && (
            <a href={selected.item.url}>{selected.item.url}</a>
          )}
          {selected.item.content_error && <p className="error">{selected.item.content_error}</p>}
          {selected.item.content_text && (
            <pre className="content">{selected.item.content_text}</pre>
          )}
          {pageCount > 0 &&
            Array.from({ length: pageCount }, (_, n) => (
              <img
                key={n}
                className="page-image"
                src={`/files/${selected.item.id}/pages/${n}`}
                alt={`${selected.item.file_name} page ${n + 1}`}
              />
            ))}
        </section>
      )}
    </main>
  );
}
