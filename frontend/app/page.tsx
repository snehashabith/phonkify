'use client'

import { useEffect, useRef, useState } from 'react'
import { Activity, Disc3, Download, Headphones, Mic, Pause, Play, RotateCcw, Upload, Volume2, Zap } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

function Deck({ side, file, onFile }: { side: 'A' | 'B'; file: File | null; onFile?: (file: File | null) => void }) {
  const inputRef = useRef<HTMLInputElement>(null)
  const name = file?.name || ''
  return <section className="deck panel">
    <div className="section-heading"><span className="eyebrow">DECK {side}</span><span className="deck-state"><span className="status-dot" /> READY</span></div>
    <div className="deck-body">
      <div className="deck-sticker">{side === 'A' ? 'INPUT' : 'OUTPUT'}</div>
      <div className="record"><Disc3 size={118} strokeWidth={0.7} /><div className="record-label">{side}</div></div>
      <div className="deck-info">
        {side === 'A' && <><button className="upload-zone" onClick={() => inputRef.current?.click()} aria-label="Upload audio">
          <Upload size={18} /><span>{name || 'DROP AUDIO FILE'}</span><small>WAV · MP3 · AIFF</small>
        </button><input ref={inputRef} type="file" accept="audio/*" hidden onChange={(event) => onFile?.(event.target.files?.[0] || null)} /></>}
        {side === 'B' && <div className="upload-zone"><Download size={18} /><span>{name || 'NO OUTPUT YET'}</span><small>MP3 PREVIEW</small></div>}
        <div className="track-line"><span>{name || 'NO INPUT LOADED'}</span><span>00:00</span></div>
        <div className="track-progress"><span /></div>
      </div>
    </div>
  </section>
}

export default function Page() {
  const [inputFile, setInputFile] = useState<File | null>(null)
  const [outputFile, setOutputFile] = useState<File | null>(null)
  const [outputUrl, setOutputUrl] = useState('')
  const [conversion, setConversion] = useState(0)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState('')
  const [playing, setPlaying] = useState(false)
  const [format, setFormat] = useState('MP3')
  const [recording, setRecording] = useState(false)
  const audioRef = useRef<HTMLAudioElement>(null)

  useEffect(() => () => { if (outputUrl) URL.revokeObjectURL(outputUrl) }, [outputUrl])

  const reset = () => {
    if (outputUrl) URL.revokeObjectURL(outputUrl)
    setInputFile(null); setOutputFile(null); setOutputUrl(''); setConversion(0)
    setPlaying(false); setError(''); setIsProcessing(false)
  }

  const selectInput = (selected: File | null) => {
    if (outputUrl) URL.revokeObjectURL(outputUrl)
    setInputFile(selected); setOutputFile(null); setOutputUrl(''); setConversion(0); setError('')
  }

  const processAudio = async () => {
    if (!inputFile || isProcessing) return
    setIsProcessing(true); setError(''); setConversion(8)
    try {
      const body = new FormData()
      body.append('file', inputFile)
      const response = await fetch(`${API_URL}/generate-phonk`, { method: 'POST', body })
      if (!response.ok) {
        const detail = await response.json().catch(() => null)
        throw new Error(detail?.detail || `Engine returned ${response.status}`)
      }
      const blob = await response.blob()
      const processed = new File([blob], `phonk_${inputFile.name.replace(/\.[^/.]+$/, '')}.mp3`, { type: 'audio/mpeg' })
      setOutputFile(processed)
      setOutputUrl(URL.createObjectURL(blob))
      setConversion(100)
    } catch (cause) {
      setConversion(0)
      setError(cause instanceof Error ? cause.message : 'Could not reach the audio engine.')
    } finally {
      setIsProcessing(false)
    }
  }

  const togglePlayback = async () => {
    if (!audioRef.current || !outputUrl) return
    if (audioRef.current.paused) { await audioRef.current.play(); setPlaying(true) }
    else { audioRef.current.pause(); setPlaying(false) }
  }

  const downloadOutput = () => {
    if (!outputUrl || !outputFile) return
    const anchor = document.createElement('a')
    anchor.href = outputUrl; anchor.download = outputFile.name; anchor.click()
  }

  const complete = Boolean(outputFile)
  return <main className="app-shell">
    <header className="topbar"><div className="brand"><span className="brand-mark"><Zap size={15} /></span><span>PHONKIFY</span><span className="version">STUDIO / 01</span></div><div className="top-status"><span className="status-dot" /> ENGINE ONLINE <span className="divider" /> 44.1 KHZ / 24 BIT</div><button className="icon-button" onClick={reset} aria-label="Reset studio"><RotateCcw size={17} /></button></header>
    <div className="workspace">
      <div className="intro"><div><div className="intro-kicker"><p className="eyebrow">AUDIO TRANSFORMATION SYSTEM</p><span className="scene-tag">ADAPTIVE DRIFT MODE</span></div><h1>MAKE IT <em>HEAVY.</em></h1></div><p className="intro-copy">Load a cut, then move the master fader to send the actual file to the local audio engine.</p></div>
      <div className="decks"><Deck side="A" file={inputFile} onFile={selectInput} /><Deck side="B" file={outputFile} /></div>
      <section className={`conversion panel ${complete ? 'is-complete' : ''}`}>
        <div className="conversion-head"><div><p className="eyebrow">MASTER PROCESSOR</p><h2>{isProcessing ? 'PROCESSING AUDIO' : complete ? 'OUTPUT READY' : 'GENERATE PHONK'}</h2></div><div className="conversion-meta"><span>{error || (isProcessing ? 'ENGINE RUNNING' : complete ? 'PROCESS COMPLETE' : 'INPUT → OUTPUT')}</span><strong>{String(conversion).padStart(3, '0')}%</strong></div></div>
        <div className="fader-wrap"><div className="fader-labels"><span>DRY</span><span>PHONK</span></div><div className="fader-track"><span style={{ width: `${conversion}%` }} /><i style={{ left: `calc(${conversion}% - 9px)` }} /></div><button className="download-button" disabled={!inputFile || isProcessing || complete} onClick={() => void processAudio()}>{isProcessing ? 'PROCESSING…' : complete ? 'OUTPUT READY' : 'GENERATE PHONK'}</button><p className="fader-hint">{error ? `Error: ${error}` : !inputFile ? 'Upload audio first.' : isProcessing ? 'The engine is separating and remixing your audio.' : complete ? 'Your processed file is ready to preview or export.' : 'Generate a real remix with the local audio engine.'}</p></div>
      </section>
      <div className="bottom-grid"><section className="record-panel panel"><div><p className="eyebrow">CAPTURE</p><h3>RECORD A NEW TAKE</h3></div><button className={`record-button ${recording ? 'recording' : ''}`} onClick={() => setRecording(!recording)}><Mic size={17} /> {recording ? 'STOP RECORDING' : 'START RECORDING'}</button></section><section className="output-panel panel"><div className="output-copy"><p className="eyebrow">EXPORT</p><h3>{outputFile?.name || 'NO OUTPUT YET'}</h3></div><select aria-label="Export format" value={format} onChange={(event) => setFormat(event.target.value)}><option>MP3</option></select><button className="download-button" disabled={!complete} onClick={downloadOutput}><Download size={17} /> EXPORT</button></section></div>
    </div>
    <footer className="player-bar"><div className="player-track"><button className="play-button" onClick={() => void togglePlayback()} disabled={!outputUrl} aria-label={playing ? 'Pause' : 'Play'}>{playing ? <Pause size={18} /> : <Play size={18} />}</button><div><span className="eyebrow">{complete ? 'PHONKIFIED_TRACK' : 'WAITING FOR INPUT'}</span><div className="player-progress"><span style={{ width: playing ? '42%' : '0%' }} /></div></div><span className="timecode">00:00 / 00:00</span></div><div className="player-volume"><Volume2 size={17} /><input aria-label="Volume" type="range" defaultValue="70" /><Headphones size={17} /></div><div className="footer-note"><Activity size={14} /> LOCAL ENGINE</div></footer>
    {outputUrl && <audio ref={audioRef} src={outputUrl} onEnded={() => setPlaying(false)} />}
  </main>
}
