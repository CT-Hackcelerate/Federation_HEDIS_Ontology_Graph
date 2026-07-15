/* eslint-disable react/forbid-prop-types */

import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import Divider from '@mui/material/Divider';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import InfoIcon from '@mui/icons-material/Info';
import ErrorIcon from '@mui/icons-material/Error';
import PersonIcon from '@mui/icons-material/Person';
import ReactMarkdown from 'react-markdown';

import styles from './patient-view.css';
import PatientLookup from '../PatientLookup/patient-lookup';

const propTypes = {
  /**
   * The patient object in context (null when nothing is loaded)
   */
  patient: PropTypes.object,
  /**
   * Array of care gap cards from the CDS API
   */
  careGaps: PropTypes.array,
  /**
   * An error message to display if the last lookup failed
   */
  errorMessage: PropTypes.string,
};

/**
 * Returns the appropriate icon and color for a CDS card indicator
 */
const getIndicatorStyle = (indicator) => {
  switch (indicator) {
    case 'critical':
      return { icon: <ErrorIcon />, color: '#c62828', bgColor: '#ffebee', borderColor: '#ef9a9a' };
    case 'warning':
      return { icon: <WarningAmberIcon />, color: '#f57c00', bgColor: '#fff3e0', borderColor: '#ffcc80' };
    case 'info':
    default:
      return { icon: <InfoIcon />, color: '#1565c0', bgColor: '#e3f2fd', borderColor: '#90caf9' };
  }
};

/**
 * Renders a single care gap card
 */
const CareGapCard = ({ card }) => {
  const indicatorStyle = getIndicatorStyle(card.indicator);
  
  return (
    <Paper 
      elevation={0} 
      sx={{ 
        p: 3, 
        mb: 2,
        backgroundColor: indicatorStyle.bgColor,
        border: `1px solid ${indicatorStyle.borderColor}`,
        borderLeft: `4px solid ${indicatorStyle.color}`,
        borderRadius: 2,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
        <Box sx={{ color: indicatorStyle.color, mt: 0.5 }}>
          {indicatorStyle.icon}
        </Box>
        <Box sx={{ flex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#1a365d' }}>
              {card.summary}
            </Typography>
            <Chip 
              label={card.indicator?.toUpperCase() || 'INFO'} 
              size="small"
              sx={{ 
                backgroundColor: indicatorStyle.color, 
                color: '#fff',
                fontWeight: 600,
                fontSize: '0.7rem',
              }} 
            />
          </Box>
          {card.detail && (
            <Box sx={{ 
              color: '#424242',
              '& p': { margin: '0.5em 0' },
              '& strong': { color: '#1a365d' },
            }}>
              <ReactMarkdown>{card.detail}</ReactMarkdown>
            </Box>
          )}
          {card.source && (
            <Typography variant="caption" sx={{ color: '#757575', display: 'block', mt: 1 }}>
              Source: {card.source.label}
            </Typography>
          )}
        </Box>
      </Box>
    </Paper>
  );
};

CareGapCard.propTypes = {
  card: PropTypes.object.isRequired,
};

/**
 * The main patient view displaying the lookup control and care gap results.
 */
export const PatientView = (props) => {
  const { patient, careGaps, errorMessage } = props;

  return (
    <div className={styles['patient-view']}>
      <Typography 
        variant="h4" 
        sx={{ 
          fontWeight: 700, 
          color: '#1a365d', 
          mb: 3,
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        <PersonIcon sx={{ fontSize: 36 }} />
        Patient Care Gap
      </Typography>
      
      <PatientLookup />

      {errorMessage && (
        <Alert severity="error" sx={{ mt: 3, borderRadius: 2 }}>{errorMessage}</Alert>
      )}

      {patient && (
        <Box sx={{ mt: 4 }}>
          <Paper 
            elevation={0} 
            sx={{ 
              p: 3, 
              mb: 3, 
              backgroundColor: '#e8f4fd',
              border: '1px solid #b3d4fc',
              borderRadius: 2,
            }}
          >
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#1a365d', mb: 1 }}>
              Patient Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Patient ID</Typography>
                <Typography variant="body1" sx={{ fontWeight: 500 }}>{patient.id}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Care Gaps Identified</Typography>
                <Typography variant="body1" sx={{ fontWeight: 500 }}>
                  {careGaps.length} {careGaps.length === 1 ? 'gap' : 'gaps'}
                </Typography>
              </Grid>
            </Grid>
          </Paper>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" sx={{ fontWeight: 600, color: '#1a365d', mb: 2 }}>
            Care Gaps & Recommendations
          </Typography>

          {careGaps.length > 0 ? (
            careGaps.map((card, index) => (
              <CareGapCard key={index} card={card} />
            ))
          ) : (
            <Paper 
              elevation={0} 
              sx={{ 
                p: 4, 
                textAlign: 'center',
                backgroundColor: '#e8f5e9',
                border: '1px solid #a5d6a7',
                borderRadius: 2,
              }}
            >
              <Typography variant="body1" sx={{ color: '#2e7d32', fontWeight: 500 }}>
                No care gaps identified for this patient.
              </Typography>
            </Paper>
          )}
        </Box>
      )}

      {!patient && !errorMessage && (
        <Box sx={{ mt: 4, textAlign: 'center', py: 6 }}>
          <PersonIcon sx={{ fontSize: 64, color: '#bdbdbd', mb: 2 }} />
          <Typography variant="h6" sx={{ color: '#757575', mb: 1 }}>
            Enter a Patient ID to Begin
          </Typography>
          <Typography variant="body2" sx={{ color: '#9e9e9e' }}>
            Search for a patient to view their care gap analysis and clinical recommendations.
          </Typography>
        </Box>
      )}
    </div>
  );
};

PatientView.propTypes = propTypes;

const mapStateToProps = (state) => ({
  patient: state.patientState.currentPatient,
  careGaps: state.patientState.careGaps || [],
  errorMessage: state.uiState.errorMessage,
});

export default connect(mapStateToProps)(PatientView);
