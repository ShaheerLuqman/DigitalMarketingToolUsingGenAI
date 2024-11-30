import React, { useState } from 'react';
import { TextField, Button, Card, CardContent, Typography, Box, Input } from '@mui/material';

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
    if (!productImage || !description.trim()) {
      alert("Please fill out all fields before submitting.");
      return;
    }
    alert("Ad submitted for generation!");
  };

  return (
    <Card sx={{ maxWidth: 600, mx: 'auto', mt: 4, p: 2, boxShadow: 3 }}>
      <CardContent>
        <Typography variant="h5" textAlign="center" gutterBottom>
          🎨 Generate Your Product Advertisement
        </Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 3, justifyContent: 'center', alignItems: 'center' }}>
          {/* File Input Button */}
          <label htmlFor="product-image">
            <Button variant="contained" component="span" fullWidth>
              Upload Product Image
            </Button>
          </label>
          <Input
            id="product-image"
            type="file"
            onChange={handleImageChange}
            accept="image/*"
            sx={{ display: 'none' }}
          />
          
          {/* Image Preview */}
          {productImage && (
            <Box sx={{ mt: 2 }}>
              <img src={URL.createObjectURL(productImage)} alt="Product Preview" style={{ maxWidth: '100%', maxHeight: '200px', objectFit: 'contain' }} />
            </Box>
          )}

          {/* Product Description Field */}
          <TextField
            label="Product Description"
            multiline
            rows={4}
            value={description}
            onChange={handleDescriptionChange}
            fullWidth
          />

          {/* Submit Button */}
          <Button type="submit" variant="contained" color="primary" size="large">
            🚀 Generate Advertisement
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ImageAdForm;
