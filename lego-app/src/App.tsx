import { useState } from 'react'
import './styles/App.scss'
import VoiceTool from './components/VoiceTool'
import { HiMiniMicrophone } from 'react-icons/hi2'
import useRealtime from './hooks/useRealtime'

function App() {
  const [inputValue, setInputValue] = useState('')
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([])
  
  const handleServerMessage = async (serverEvent: any) => {
    console.log('Server event:', serverEvent)
    if (serverEvent.type === 'message' && serverEvent.content) {
      setMessages(prev => [...prev, {
        role: serverEvent.role || 'assistant',
        content: serverEvent.content
      }])
    }
  }

  const user = { key: 'mobile-user', name: 'Mobile User' }
  const { toggleRealtime, analyzer, sendRealtime, callState } = useRealtime(user, handleServerMessage)

  const handleVoice = async () => {
    if (callState === 'idle') {
      console.log('Starting voice call')
    } else if (callState === 'call') {
      const response = confirm('End voice call?')
      if (!response) return
    }
    toggleRealtime()
  }

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && inputValue.trim()) {
      sendTextMessage(inputValue)
      setInputValue('')
    }
  }

  const sendTextMessage = async (text: string) => {
    setMessages(prev => [...prev, { role: 'user', content: text }])
    await sendRealtime({
      id: crypto.randomUUID(),
      type: 'message',
      role: 'user',
      content: text,
    })
  }

  return (
    <div className="app">
      <div className="header">
        <div className="logo">
          <div className="lego-brick" />
          <h1>LEGO ROBOT</h1>
        </div>
        <div className="subtitle">Everything is Awesome! 🎵</div>
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome">
            <HiMiniMicrophone size={64} className="welcome-icon" />
            <h2>Ready to Build!</h2>
            <p>Tap the mic or type a command to control your LEGO robot</p>
          </div>
        ) : (
          <div className="messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-bubble">
                  {msg.content}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="input-area">
        <input
          type="text"
          placeholder="Type a command..."
          className="text-input"
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onKeyDown={handleInputKeyDown}
        />
        <VoiceTool
          onClick={handleVoice}
          callState={callState}
          analyzer={analyzer}
        />
      </div>
    </div>
  )
}

export default App
