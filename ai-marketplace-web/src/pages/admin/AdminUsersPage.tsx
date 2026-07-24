import { useEffect, useState } from 'react'
import { adminApi, type AdminUser } from '@/api/endpoints'
import { Button } from '@/components/common/Button'
import { Badge } from '@/components/common/Feedback'

export function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    adminApi.listUsers().then((data) => {
      setUsers(data)
      setIsLoading(false)
    })
  }, [])

  async function toggleBan(u: AdminUser) {
    const reason = u.is_banned ? undefined : prompt('سبب الحظر (اختياري):') || undefined
    const updated = await adminApi.banUser(u.id, !u.is_banned, reason)
    setUsers((prev) => prev.map((x) => (x.id === u.id ? updated : x)))
  }

  if (isLoading) return <p className="text-[var(--color-text-secondary)]">جاري التحميل...</p>

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-right text-[var(--color-text-secondary)] border-b border-[var(--color-border)]">
            <th className="py-2 px-3 font-medium">الاسم</th>
            <th className="py-2 px-3 font-medium">البريد</th>
            <th className="py-2 px-3 font-medium">الحالة</th>
            <th className="py-2 px-3 font-medium">تاريخ الانضمام</th>
            <th className="py-2 px-3 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id} className="border-b border-[var(--color-border)]">
              <td className="py-3 px-3">{u.full_name}</td>
              <td className="py-3 px-3 text-[var(--color-text-secondary)]">{u.email}</td>
              <td className="py-3 px-3">
                {u.is_banned ? <Badge tone="danger">محظور</Badge> : <Badge tone="success">نشط</Badge>}
              </td>
              <td className="py-3 px-3 text-[var(--color-text-secondary)]">{new Date(u.created_at).toLocaleDateString('ar')}</td>
              <td className="py-3 px-3">
                <Button size="sm" variant={u.is_banned ? 'secondary' : 'danger'} onClick={() => toggleBan(u)}>
                  {u.is_banned ? 'فك الحظر' : 'حظر'}
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
