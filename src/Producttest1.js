import React, { useState } from 'react';
import { TextField, Button, Card, CardContent, Typography, Box } from '@mui/material';

const ImageAdForm = () => {
  const [productImage, setProductImage] = useState(null);
  const [description, setDescription] = useState('');

  const handleImageChange = (event) => {
    setProductImage(event.target.files[0]);
  };

  const handleDescriptionChange = (event) => {
    setDescription(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    alert("Ad submitted for generation!");
  };

  return (
    <Card sx={{ maxWidth: 600, mx: 'auto', mt: 4, p: 2, boxShadow: 3 }}>
      <CardContent>
        <Typography variant="h5" textAlign="center" gutterBottom>
          🎨 Generate Your Product Advertisement
        </Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <input
            type="file"
            onChange={handleImageChange}
            accept="image/*"
            style={{ display: 'block', marginBottom: '1rem' }}
          />
          <TextField
            label="Product Description"
            multiline
            rows={4}
            value={description}
            onChange={handleDescriptionChange}
          />
          <Button type="submit" variant="contained" color="primary" size="large">
            🚀 Generate Advertisement
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ImageAdForm;
