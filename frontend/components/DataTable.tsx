import { useState, useMemo } from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Paper,
  Box,
  Chip,
  Checkbox,
} from '@mui/material'

export interface Column<T> {
  id: string
  label: string
  sortable?: boolean
  render?: (row: T) => React.ReactNode
  align?: 'left' | 'center' | 'right'
  width?: string | number
}

interface DataTableProps<T> {
  data: T[]
  columns: Column<T>[]
  rowsPerPageOptions?: number[]
  defaultRowsPerPage?: number
  onRowClick?: (row: T) => void
  getRowId?: (row: T) => string | number
  selectable?: boolean
  selectedRows?: Set<string | number>
  onSelectionChange?: (selected: Set<string | number>) => void
}

type Order = 'asc' | 'desc'

export function DataTable<T extends Record<string, any>>({
  data,
  columns,
  rowsPerPageOptions = [10, 25, 50, 100],
  defaultRowsPerPage = 10,
  onRowClick,
  getRowId = (row) => row.id,
  selectable = false,
  selectedRows = new Set(),
  onSelectionChange,
}: DataTableProps<T>) {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(defaultRowsPerPage)
  const [orderBy, setOrderBy] = useState<string>('')
  const [order, setOrder] = useState<Order>('asc')

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!onSelectionChange) return

    if (event.target.checked) {
      const newSelected = new Set(data.map(row => getRowId(row)))
      onSelectionChange(newSelected)
    } else {
      onSelectionChange(new Set())
    }
  }

  const handleSelectRow = (rowId: string | number) => {
    if (!onSelectionChange) return

    const newSelected = new Set(selectedRows)
    if (newSelected.has(rowId)) {
      newSelected.delete(rowId)
    } else {
      newSelected.add(rowId)
    }
    onSelectionChange(newSelected)
  }

  const isSelected = (rowId: string | number) => selectedRows.has(rowId)
  const isAllSelected = data.length > 0 && selectedRows.size === data.length

  const handleRequestSort = (columnId: string) => {
    const isAsc = orderBy === columnId && order === 'asc'
    setOrder(isAsc ? 'desc' : 'asc')
    setOrderBy(columnId)
  }

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  // Sorting logic
  const sortedData = useMemo(() => {
    if (!orderBy) return data

    return [...data].sort((a, b) => {
      const aValue = a[orderBy]
      const bValue = b[orderBy]

      // Handle null/undefined
      if (aValue == null) return 1
      if (bValue == null) return -1

      // Handle dates
      if (aValue instanceof Date && bValue instanceof Date) {
        return order === 'asc'
          ? aValue.getTime() - bValue.getTime()
          : bValue.getTime() - aValue.getTime()
      }

      // Handle strings
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return order === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }

      // Handle numbers
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return order === 'asc' ? aValue - bValue : bValue - aValue
      }

      return 0
    })
  }, [data, orderBy, order])

  // Pagination
  const paginatedData = useMemo(() => {
    const startIndex = page * rowsPerPage
    return sortedData.slice(startIndex, startIndex + rowsPerPage)
  }, [sortedData, page, rowsPerPage])

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      <TableContainer>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              {selectable && (
                <TableCell
                  padding="checkbox"
                  sx={{
                    fontWeight: 600,
                    backgroundColor: 'grey.50'
                  }}
                >
                  <Checkbox
                    color="primary"
                    indeterminate={selectedRows.size > 0 && selectedRows.size < data.length}
                    checked={isAllSelected}
                    onChange={handleSelectAll}
                  />
                </TableCell>
              )}
              {columns.map((column) => (
                <TableCell
                  key={column.id}
                  align={column.align || 'left'}
                  sx={{
                    fontWeight: 600,
                    width: column.width,
                    backgroundColor: 'grey.50'
                  }}
                >
                  {column.sortable ? (
                    <TableSortLabel
                      active={orderBy === column.id}
                      direction={orderBy === column.id ? order : 'asc'}
                      onClick={() => handleRequestSort(column.id)}
                    >
                      {column.label}
                    </TableSortLabel>
                  ) : (
                    column.label
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedData.map((row) => {
              const rowId = getRowId(row)
              const rowSelected = isSelected(rowId)

              return (
                <TableRow
                  key={rowId}
                  hover
                  onClick={() => !selectable && onRowClick?.(row)}
                  selected={rowSelected}
                  sx={{
                    cursor: onRowClick && !selectable ? 'pointer' : 'default',
                    '&:hover': {
                      backgroundColor: onRowClick && !selectable ? 'action.hover' : 'inherit'
                    }
                  }}
                >
                  {selectable && (
                    <TableCell padding="checkbox">
                      <Checkbox
                        color="primary"
                        checked={rowSelected}
                        onChange={() => handleSelectRow(rowId)}
                      />
                    </TableCell>
                  )}
                  {columns.map((column) => (
                    <TableCell key={column.id} align={column.align || 'left'}>
                      {column.render ? column.render(row) : row[column.id]}
                    </TableCell>
                  ))}
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </TableContainer>

      {data.length > rowsPerPageOptions[0] && (
        <TablePagination
          rowsPerPageOptions={rowsPerPageOptions}
          component="div"
          count={data.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      )}

      {data.length === 0 && (
        <Box sx={{ p: 3, textAlign: 'center', color: 'text.secondary' }}>
          No data available
        </Box>
      )}
    </Paper>
  )
}
