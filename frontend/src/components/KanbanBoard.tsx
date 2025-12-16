import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd'
import { Lead } from '../types'
import { useLanguage } from '../contexts/LanguageContext'
import LeadCard from './LeadCard'

interface KanbanBoardProps {
  leads: Lead[]
  onStatusChange: (leadId: number, newStatus: Lead['status']) => void
  onLeadClick: (lead: Lead) => void
}

export default function KanbanBoard({ leads, onStatusChange, onLeadClick }: KanbanBoardProps) {
  const { language } = useLanguage()

  const columns: Array<{ id: Lead['status']; title: string; color: string }> = [
    {
      id: 'new',
      title: language === 'fr' ? 'Nouveau' : 'New',
      color: 'bg-slate-100 border-slate-300',
    },
    {
      id: 'contacted',
      title: language === 'fr' ? 'Contacté' : 'Contacted',
      color: 'bg-blue-100 border-blue-300',
    },
    {
      id: 'qualified',
      title: language === 'fr' ? 'Qualifié' : 'Qualified',
      color: 'bg-green-100 border-green-300',
    },
    {
      id: 'negotiating',
      title: language === 'fr' ? 'Négociation' : 'Negotiating',
      color: 'bg-amber-100 border-amber-300',
    },
    {
      id: 'converted',
      title: language === 'fr' ? 'Converti' : 'Converted',
      color: 'bg-purple-100 border-purple-300',
    },
    {
      id: 'lost',
      title: language === 'fr' ? 'Perdu' : 'Lost',
      color: 'bg-red-100 border-red-300',
    },
  ]

  const getLeadsByStatus = (status: Lead['status']) => {
    return leads.filter((lead) => lead.status === status)
  }

  const handleDragEnd = (result: DropResult) => {
    const { destination, draggableId } = result

    if (!destination) return

    const leadId = parseInt(draggableId.replace('lead-', ''))
    const newStatus = destination.droppableId as Lead['status']

    onStatusChange(leadId, newStatus)
  }

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <div className="flex gap-4 overflow-x-auto pb-4">
        {columns.map((column) => {
          const columnLeads = getLeadsByStatus(column.id)

          return (
            <div key={column.id} className="flex-shrink-0 w-80">
              {/* Column Header */}
              <div className={`${column.color} rounded-t-xl border-2 p-3`}>
                <h3 className="font-semibold text-slate-900 flex items-center justify-between">
                  <span>{column.title}</span>
                  <span className="bg-white/80 px-2 py-0.5 rounded-full text-xs">
                    {columnLeads.length}
                  </span>
                </h3>
              </div>

              {/* Column Content */}
              <Droppable droppableId={column.id}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={`${column.color} border-2 border-t-0 rounded-b-xl p-2 min-h-[500px] space-y-2 transition-colors ${
                      snapshot.isDraggingOver ? 'bg-opacity-50' : ''
                    }`}
                  >
                    {columnLeads.map((lead, index) => (
                      <Draggable
                        key={lead.id}
                        draggableId={`lead-${lead.id}`}
                        index={index}
                      >
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className={`${
                              snapshot.isDragging ? 'opacity-50 rotate-2' : ''
                            }`}
                          >
                            <LeadCard lead={lead} onClick={() => onLeadClick(lead)} />
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}

                    {/* Empty State */}
                    {columnLeads.length === 0 && (
                      <div className="text-center py-8 text-slate-400 text-sm">
                        {language === 'fr'
                          ? 'Aucun prospect'
                          : 'No leads'}
                      </div>
                    )}
                  </div>
                )}
              </Droppable>
            </div>
          )
        })}
      </div>
    </DragDropContext>
  )
}
