import React from 'react';
import { Box, Table, TableBody, TableCell, TableHead, TableRow, Button } from '@mui/material';

function UploadManagement() {
  const uploads = [
    { id: 1, title: 'Sample Upload 1', date: '17-04-2025', executed: true },
    { id: 2, title: 'Sample Upload 2', date: '10-12-2024', executed: false },
  ];

  return (
    <Box sx={{ padding: 3 }}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Title</TableCell>
            <TableCell>Date</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {uploads.map((upload) => (
            <TableRow key={upload.id}>
              <TableCell>{upload.title}</TableCell>
              <TableCell>{upload.date}</TableCell>
              <TableCell>{upload.executed ? 'Archived' : 'Scheduled'}</TableCell>
              <TableCell>
                {!upload.executed && (
                  <>
                    <Button variant="outlined" sx={{ marginRight: 1 }}>
                      Edit
                    </Button>
                    <Button variant="outlined" color="error">
                      Delete
                    </Button>
                  </>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Box>
  );
}

export default UploadManagement;
