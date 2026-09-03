'use client'

import { useRef, useState } from 'react'
import { Activity, Disc3, Download, Headphones, Mic, Pause, Play, RotateCcw, Upload, Volume2, Zap } from 'lucide-react'

function Deck({ side, file, onFile }: { side: 'A' | 'B'; file: string; onFile: (name: string) => void }) {
  const inputRef = useRef<HTMLInputElement>(null)
  return <section className="deck panel">
    <div className="section-heading"><span className="eyebrow">DECK {side}</span><span className="deck-state"><span className="status-dot" /> READY</span></div>
    <div className="deck-body">
      <div className="deck-sticker">{side === 'A' ? 'INPUT' : 'OUTPUT'}</div>
      <div className="record"><Disc3 size={118} strokeWidth={0.7} /><div className="record-label">{side}</div></div>
      <div className="deck-info">
        <button className="upload-zone" onClick={() => inputRef.current?.click()} aria-label={`Upload audio to deck ${side}`}>
          <Upload size={18} /><span>{file || 'DROP AUDIO FILE'}</span><small>WAV · MP3 · AIFF</small>
        </button>
        <input ref={inputRef} type="file" accept="audio/*" hidden onChange={(event) => onFile(event.target.files?.[0]?.name || '')} />
        <div className="track-line"><span>{file || 'NO INPUT LOADED'}</span><span>00:00</span></div>
        <div className="track-progress"><span /></div>
      </div>
    </div>
  </section>
}

export default function Page() {
  const [file, setFile] = useState('')
  const [conversion, setConversion] = useState(0)
  const [converted, setConverted] = useState(false)
  const [playing, setPlaying] = useState(false)
  const [format, setFormat] = useState('WAV')
  const [recording, setRecording] = useState(false)

  const handleConversion = (value: number) => {
    setConversion(value)
    if (value >= 100) setConverted(true)
  }
  const reset = () => { setConversion(0); setConverted(false); setPlaying(false); setFile('') }

  return <main className="app-shell">
    <header className="topbar"><div className="brand"><span className="brand-mark"><Zap size={15} /></span><span>PHONKIFY</span><span className="version">STUDIO / 01</span></div><div className="top-status"><span className="status-dot" /> ENGINE ONLINE <span className="divider" /> 44.1 KHZ / 24 BIT</div><button className="icon-button" onClick={reset} aria-label="Reset studio"><RotateCcw size={17} /></button></header>
    <div className="workspace">
      <div className="intro"><div><div className="intro-kicker"><p className="eyebrow">AUDIO TRANSFORMATION SYSTEM</p><span className="scene-tag">NIGHT RUN / 140 BPM</span></div><h1>MAKE IT <em>HEAVY.</em></h1></div><p className="intro-copy">Load a cut, push the master fader, and turn clean input into a tape-worn drift phonk weapon.</p></div>
      <div className="decks"><Deck side="A" file={file} onFile={setFile} /><Deck side="B" file={file ? 'PHONK OUTPUT / PREVIEW' : ''} onFile={() => {}} /></div>
      <section className={`conversion panel ${converted ? 'is-complete' : ''}`}>
        <div className="conversion-head"><div><p className="eyebrow">MASTER PROCESSOR</p><h2>{converted ? 'OUTPUT READY' : 'DRAG TO PHONKIFY'}</h2></div><div className="conversion-meta"><span>{converted ? 'PROCESS COMPLETE' : conversion > 0 ? 'PROCESS ARMED' : 'INPUT → OUTPUT'}</span><strong>{String(conversion).padStart(3, '0')}%</strong></div></div>
        <div className="fader-wrap"><div className="fader-labels"><span>DRY</span><span>PHONK</span></div><input className="master-fader" aria-label="Drag to phonkify" type="range" min="0" max="100" value={conversion} onChange={(event) => handleConversion(Number(event.target.value))} /><div className="fader-track"><span style={{ width: `${conversion}%` }} /><i style={{ left: `calc(${conversion}% - 9px)` }} /></div><p className="fader-hint">{converted ? 'Your processed file is ready to export.' : 'Pull the fader all the way right to commit the transformation.'}</p></div>
      </section>
      <div className="bottom-grid"><section className="record-panel panel"><div><p className="eyebrow">CAPTURE</p><h3>RECORD A NEW TAKE</h3></div><button className={`record-button ${recording ? 'recording' : ''}`} onClick={() => setRecording(!recording)}><Mic size={17} /> {recording ? 'STOP RECORDING' : 'START RECORDING'}</button></section><section className="output-panel panel"><div className="output-copy"><p className="eyebrow">EXPORT</p><h3>{converted ? 'PHONKIFIED_TRACK.WAV' : 'NO OUTPUT YET'}</h3></div><select aria-label="Export format" value={format} onChange={(event) => setFormat(event.target.value)}><option>WAV</option><option>MP3</option><option>AIFF</option></select><button className="download-button" disabled={!converted} onClick={() => alert(`Exporting ${format}`)}><Download size={17} /> EXPORT</button></section></div>
    </div>
    <footer className="player-bar"><div className="player-track"><button className="play-button" onClick={() => setPlaying(!playing)} aria-label={playing ? 'Pause' : 'Play'}>{playing ? <Pause size={18} /> : <Play size={18} />}</button><div><span className="eyebrow">{converted ? 'PHONKIFIED_TRACK' : 'WAITING FOR INPUT'}</span><div className="player-progress"><span style={{ width: playing ? '42%' : '0%' }} /></div></div><span className="timecode">00:00 / 00:00</span></div><div className="player-volume"><Volume2 size={17} /><input aria-label="Volume" type="range" defaultValue="70" /><Headphones size={17} /></div><div className="footer-note"><Activity size={14} /> NO EXTERNAL SERVICES</div></footer>
  </main>
}
