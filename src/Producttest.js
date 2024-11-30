import React, { useState } from 'react';

const ImageAdForm = () => {
  const [productImage, setProductImage] = useState(null);
  const [description, setDescription] = useState('');
  const [generatedAd, setGeneratedAd] = useState(null);

  const handleImageChange = (event) => {
    setProductImage(event.target.files[0]);
  };

  const handleDescriptionChange = (event) => {
    setDescription(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!productImage || !description) {
      alert("Please provide both an image and a description.");
      return;
    }

    // Simulate sending data to backend
    console.log("Image:", productImage);
    console.log("Description:", description);

    // Add your image generation logic here
    // const adImage = await generateAd(productImage, description);
    // setGeneratedAd(adImage);

    alert("Ad submitted for generation!");
  };

  return (
    <div style={styles.container}>
      <h2>Generate Product Advertisement</h2>
      <form onSubmit={handleSubmit} style={styles.form}>
        <label>
          Upload Product Image:
          <input type="file" onChange={handleImageChange} accept="image/*" />
        </label>
        <label>
          Product Description:
          <textarea 
            value={description} 
            onChange={handleDescriptionChange} 
            placeholder="Enter a brief description of the product"
            rows="4"
            style={styles.textArea}
          />
        </label>
        <button type="submit" style={styles.submitButton}>Generate Advertisement</button>
      </form>
      {generatedAd && (
        <div style={styles.adPreview}>
          <h3>Generated Advertisement Preview:</h3>
          <img src={generatedAd} alt="Generated Ad" style={styles.image} />
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '600px',
    margin: '0 auto',
    padding: '20px',
    textAlign: 'center',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    alignItems: 'center',
  },
  textArea: {
    width: '100%',
    resize: 'vertical',
  },
  submitButton: {
    padding: '10px 20px',
    fontSize: '16px',
  },
  adPreview: {
    marginTop: '20px',
  },
  image: {
    maxWidth: '100%',
    height: 'auto',
  },
};

export default ImageAdForm;


