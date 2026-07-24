import { useEffect, useState } from 'react'
import { adminApi, type AdminUser } from '@/api/endpoints'
import { Button } from '@/components/common/Button'
import { Badge } from '@/components/common/Feedback'
import { useToast } from '@/components/common/Toast'

export function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const toast = useToast()

  useEffect(() => {
    adminApi.listUsers().then((data) => {
      setUsers(data)
      setIsLoading(false)
    })
  }, [])

  async function toggleBan(u: AdminUser) {
    const reason = u.is_banned ? undefined : prompt('Ban reason (optional):') || undefined
    try {
      const updated = await adminApi.banUser(u.id, !u.is_banned, reason)
      setUsers((prev) => prev.map((x) => (x.id === u.id ? updated : x)))
      toast.success(u.is_banned ? `${u.full_name} has been unbanned` : `${u.full_name} has been banned`)
    } catch {
      toast.error(`Could not ${u.is_banned ? 'unban' : 'ban'} ${u.full_name} — please try again`)
    }
  }

  if (isLoading) return <p className="text-[var(--color-text-secondary)]">Loading...</p>

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-[var(--color-text-secondary)] border-b border-[var(--color-border)]">
            <th className="py-2 px-3 font-medium">Name</th>
            <th className="py-2 px-3 font-medium">Email</th>
            <th className="py-2 px-3 font-medium">Status</th>
            <th className="py-2 px-3 font-medium">Joined</th>
            <th className="py-2 px-3 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id} className="border-b border-[var(--color-border)]">
              <td className="py-3 px-3">{u.full_name}</td>
              <td className="py-3 px-3 text-[var(--color-text-secondary)]">{u.email}</td>
              <td className="py-3 px-3">
                {u.is_banned ? <Badge tone="danger">Banned</Badge> : <Badge tone="success">Active</Badge>}
              </td>
              <td className="py-3 px-3 text-[var(--color-text-secondary)]">{new Date(u.created_at).toLocaleDateString('en-US')}</td>
              <td className="py-3 px-3">
                <Button size="sm" variant={u.is_banned ? 'secondary' : 'danger'} onClick={() => toggleBan(u)}>
                  {u.is_banned ? 'Unban' : 'Ban'}
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
