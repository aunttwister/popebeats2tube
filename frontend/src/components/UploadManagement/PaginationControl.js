import React from 'react';
import { Pagination } from '@mui/material';

function PaginationControl({ totalPages, currentPage, onPageChange }) {
  return (
    <div className="upload-management-pagination">
      <Pagination
        count={totalPages}
        page={currentPage}
        onChange={onPageChange}
        color="primary"
      />
    </div>
  );
}

export default PaginationControl;
