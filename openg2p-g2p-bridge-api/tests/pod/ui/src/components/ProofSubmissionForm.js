import React, { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import './ProofSubmissionForm.css';
import { config } from '../config';

const ProofSubmissionForm = () => {
  const [formData, setFormData] = useState({
    disbursement_id: '',
    agent_id: '',
    beneficiary_id: '',
    latitude: '',
    longitude: '',
    geojson: '',
    proofs: '',
    photos: [],
    descriptions: [''],
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [previewUrls, setPreviewUrls] = useState([]);

  // Handle text/number/geojson/proofs input
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Handle file input (multiple)
  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > config.maxPhotos) {
      toast.error(`Maximum ${config.maxPhotos} photos allowed.`);
      return;
    }
    for (const file of files) {
      if (!file.type.startsWith('image/')) {
        toast.error('All uploaded files must be images.');
        return;
      }
    }
    setFormData((prev) => ({
      ...prev,
      photos: files,
      descriptions: Array(files.length).fill(''),
    }));
    const previews = files.map((file) => URL.createObjectURL(file));
    setPreviewUrls(previews);
  };

  const handleDescriptionChange = (idx, value) => {
    setFormData((prev) => {
      const descriptions = [...prev.descriptions];
      descriptions[idx] = value;
      return { ...prev, descriptions };
    });
  };

  // Validate JSON LD before submit
  const isValidJsonLd = (str) => {
    try {
      const obj = JSON.parse(str);
      return obj && obj['@context'] && obj['@type'];
    } catch (e) {
      return false;
    }
  };

  // Form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    const { disbursement_id, agent_id, beneficiary_id, latitude, longitude, photos, proofs } = formData;
    if (!disbursement_id || !beneficiary_id || !latitude || !longitude) {
      toast.error('All fields except photo descriptions, geojson, and proofs are mandatory.');
      return;
    }
    if (!photos || photos.length === 0) {
      toast.error('At least one photo is required.');
      return;
    }
    if (photos.length > config.maxPhotos) {
      toast.error(`Maximum ${config.maxPhotos} photos allowed.`);
      return;
    }
    if (proofs && !isValidJsonLd(proofs)) {
      toast.error('Proofs must be valid JSON LD and include @context and @type fields.');
      return;
    }
    const submitData = new FormData();
    submitData.append('disbursement_id', disbursement_id);
    submitData.append('agent_id', agent_id);
    submitData.append('beneficiary_id', beneficiary_id);
    submitData.append('latitude', latitude);
    submitData.append('longitude', longitude);
    if (formData.geojson) submitData.append('geojson', formData.geojson);
    if (formData.proofs) submitData.append('proofs', formData.proofs);
    photos.forEach((file) => submitData.append('photos', file));
    if (formData.descriptions.some((desc) => desc && desc.trim() !== '')) {
      formData.descriptions.forEach((desc) => submitData.append('descriptions', desc));
    }
    setIsSubmitting(true);
    try {
      const response = await axios.post(config.api.submitProof, submitData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      if (response.status === 200) {
        toast.success('Proof submitted successfully!');
        setFormData({
          disbursement_id: '',
          agent_id: '',
          beneficiary_id: '',
          latitude: '',
          longitude: '',
          geojson: '',
          proofs: '',
          photos: [],
          descriptions: [''],
        });
        setPreviewUrls([]);
      }
    } catch (error) {
      const err = error.response;
      const code = err?.headers?.['x-error-code'] || err?.data?.error_code;
      const detail = err?.data?.detail || 'Failed to submit proof. Please try again.';
      if (code) {
        toast.error(`${code}: ${detail}`);
      } else {
        toast.error(detail);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="form-container">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="disbursement_id">Disbursement ID<span className="required">*</span></label>
          <input
            type="text"
            id="disbursement_id"
            name="disbursement_id"
            value={formData.disbursement_id}
            onChange={handleInputChange}
            placeholder="Enter disbursement ID"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="agent_id">Agent ID</label>
          <input
            type="text"
            id="agent_id"
            name="agent_id"
            value={formData.agent_id}
            onChange={handleInputChange}
            placeholder="Enter agent ID"
          />
        </div>
        <div className="form-group">
          <label htmlFor="beneficiary_id">Beneficiary ID<span className="required">*</span></label>
          <input
            type="text"
            id="beneficiary_id"
            name="beneficiary_id"
            value={formData.beneficiary_id}
            onChange={handleInputChange}
            placeholder="Enter beneficiary ID"
            required
          />
        </div>
        <div className="form-row">
          <div className="form-group geo">
            <label htmlFor="latitude">Latitude<span className="required">*</span></label>
            <input
              type="number"
              step="any"
              id="latitude"
              name="latitude"
              value={formData.latitude}
              onChange={handleInputChange}
              placeholder="e.g. 28.6139"
              required
            />
          </div>
          <div className="form-group geo">
            <label htmlFor="longitude">Longitude<span className="required">*</span></label>
            <input
              type="number"
              step="any"
              id="longitude"
              name="longitude"
              value={formData.longitude}
              onChange={handleInputChange}
              placeholder="e.g. 77.2090"
              required
            />
          </div>
        </div>
        <div className="form-group">
          <label htmlFor="geojson">GeoJSON (optional)</label>
          <textarea
            id="geojson"
            name="geojson"
            value={formData.geojson}
            onChange={handleInputChange}
            placeholder='{"type": "Point", "coordinates": [77.2090, 28.6139]}'
            rows={2}
          />
        </div>
        <div className="form-group">
          <label htmlFor="proofs">Proofs (optional, JSON LD)</label>
          <textarea
            id="proofs"
            name="proofs"
            value={formData.proofs}
            onChange={handleInputChange}
            placeholder='{"@context": "https://schema.org", "@type": "Proof", "proofValue": "abc123"}'
            rows={3}
          />
        </div>
        <div className="form-group">
          <label htmlFor="photos">Proof Images<span className="required">*</span> (max {config.maxPhotos})</label>
          <input
            type="file"
            id="photos"
            name="photos"
            accept="image/*"
            multiple
            onChange={handleFileChange}
            required
          />
          <div className="photo-previews">
            {previewUrls.map((url, idx) => (
              <div className="image-preview" key={idx}>
                <img src={url} alt={`Preview ${idx + 1}`} />
                <input
                  type="text"
                  className="photo-description"
                  placeholder="Description (optional)"
                  value={formData.descriptions[idx] || ''}
                  onChange={e => handleDescriptionChange(idx, e.target.value)}
                />
              </div>
            ))}
          </div>
        </div>
        <button
          type="submit"
          className="submit-button"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Submitting...' : 'Submit Proof'}
        </button>
      </form>
    </div>
  );
};

export default ProofSubmissionForm;
