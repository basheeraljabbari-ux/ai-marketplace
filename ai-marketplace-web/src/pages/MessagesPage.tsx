import { useEffect, useState, useRef, type FormEvent } from 'react'
import { useParams, Link } from 'react-router-dom'
import { messagingApi } from '@/api/endpoints'
import { EmptyState } from '@/components/common/Feedback'
import { useAuth } from '@/context/AuthContext'

interface ConversationSummary {
  id: string
  last_message_preview: string | null
  last_message_at: string | null
  unread_count: number
}
interface MessageItem {
  id: string
  sender_id: string | null
  content: string | null
  created_at: string
}

export function MessagesPage() {
  const { conversationId } = useParams<{ conversationId: string }>()
  const { user } = useAuth()
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [messages, setMessages] = useState<MessageItem[]>([])
  const [text, setText] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagingApi.listConversations().then(setConversations)
  }, [])

  useEffect(() => {
    if (!conversationId) return
    messagingApi.listMessages(conversationId).then(setMessages)
  }, [conversationId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSend(e: FormEvent) {
    e.preventDefault()
    if (!text.trim() || !conversationId) return
    const msg = await messagingApi.sendMessage(conversationId, text)
    setMessages((prev) => [...prev, msg])
    setText('')
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="grid grid-cols-1 md:grid-cols-[280px_1fr] gap-6 h-[70vh]">
        {/* Conversation list */}
        <aside className="border border-[var(--color-border)] rounded-xl overflow-y-auto">
          {conversations.length === 0 ? (
            <div className="p-6"><EmptyState title="No conversations" description="Message a seller from any listing page" /></div>
          ) : (
            conversations.map((c) => (
              <Link
                key={c.id}
                to={`/messages/${c.id}`}
                className={`block p-4 border-b border-[var(--color-border)] hover:bg-[var(--color-surface)] transition-colors ${
                  conversationId === c.id ? 'bg-[var(--color-surface)]' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <p className="text-sm truncate">{c.last_message_preview || 'New conversation'}</p>
                  {c.unread_count > 0 && (
                    <span className="w-5 h-5 rounded-full bg-[var(--color-accent)] text-[#0F0F0F] text-xs flex items-center justify-center shrink-0">
                      {c.unread_count}
                    </span>
                  )}
                </div>
              </Link>
            ))
          )}
        </aside>

        {/* Thread */}
        <div className="border border-[var(--color-border)] rounded-xl flex flex-col">
          {!conversationId ? (
            <div className="flex-1 flex items-center justify-center text-[var(--color-text-secondary)]">Select a conversation</div>
          ) : (
            <>
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {messages.map((m) => (
                  <div key={m.id} className={`flex ${m.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}>
                    {/* Sent bubbles are a neutral grey, not gold: in a long thread they'd
                        otherwise fill most of the screen and dilute the accent. The border
                        carries the distinction from received bubbles that the fill alone
                        no longer makes, since the two tones sit close together. */}
                    <div
                      className={`max-w-[70%] rounded-2xl px-4 py-2 text-sm text-white ${
                        m.sender_id === user?.id
                          ? 'bg-[#2A2E35] border border-white/10'
                          : 'bg-[var(--color-surface)]'
                      }`}
                    >
                      {m.content}
                    </div>
                  </div>
                ))}
                <div ref={bottomRef} />
              </div>
              <form onSubmit={handleSend} className="border-t border-[var(--color-border)] p-3 flex gap-2">
                <input
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Type a message..."
                  className="flex-1 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
                />
                <button type="submit" className="w-10 h-10 rounded-full bg-[var(--color-accent)] text-[#0F0F0F] flex items-center justify-center shrink-0">➤</button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
