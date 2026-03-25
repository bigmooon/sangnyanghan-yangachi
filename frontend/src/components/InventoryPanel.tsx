import type { Item } from '../types/game'

interface Props {
  inventory: Item[]
  onUseItem: (item_id: string) => void
  disabled: boolean
}

export function InventoryPanel({ inventory, onUseItem, disabled }: Props) {
  return (
    <div className="inventory-panel pixel-box">
      <span className="pixel-label">INVENTORY ({inventory.length}/5)</span>
      {inventory.length === 0 ? (
        <p className="empty-inv">-- 비어있음 --</p>
      ) : (
        <div className="inv-grid">
          {inventory.map(item => (
            <button
              key={item.id}
              className="inv-item"
              onClick={() => onUseItem(item.id)}
              disabled={disabled}
              title={item.description ?? item.name}
            >
              <span className="inv-icon">{item.icon}</span>
              <span className="inv-name">{item.name}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
