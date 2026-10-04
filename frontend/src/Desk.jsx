import { useEffect, useState } from "react";
import { createLink, getFile, getFiles, getLink, getLinks, logout, uploadFile } from "./api";

export default function Desk({ user, onLogout }) {
  const [links, setLinks] = useState([]);
  const [files, setFiles] = useState([]);
  const [url, setUrl] = useState("");
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);

  async function load() {
    const [linkData, fileData] = await Promise.all([getLinks(), getFiles()]);
    setLinks(linkData.links);
    setFiles(fileData.files);
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

  async function openItem(kind, id) {
    setError("");
    try {
      const data = kind === "file" ? await getFile(id) : await getLink(id);
      setSelected({ kind, item: data.file || data.link });
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
        </section>
      )}
    </main>
  );
}
