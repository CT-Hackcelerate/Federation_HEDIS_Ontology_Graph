import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import Backdrop from '@mui/material/Backdrop';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import ApiIcon from '@mui/icons-material/Api';

import styles from './main-view.css';
import Header from '../Header/header';
import PatientView from '../PatientView/patient-view';
import { appVersion } from '../../config/fhir-config';

const propTypes = {
  /**
   * Flag to determine if a network call is in flight, used to display a loading spinner
   */
  isLoadingData: PropTypes.bool.isRequired,
  /**
   * API metadata for footer display
   */
  apiMetadata: PropTypes.object,
};

/**
 * Footer component displaying API response details
 */
const ApiFooter = ({ metadata }) => {
  if (!metadata) {
    return (
      <Box 
        component="footer" 
        sx={{ 
          backgroundColor: '#1a365d',
          color: '#fff',
          py: 2,
          px: 3,
          mt: 'auto',
        }}
      >
        <Box sx={{ maxWidth: 900, mx: 'auto', display: 'flex', alignItems: 'center', gap: 1 }}>
          <ApiIcon sx={{ fontSize: 18, opacity: 0.7 }} />
          <Typography variant="caption" sx={{ opacity: 0.7 }}>
          CDS Hooks Sandbox v{appVersion}
          </Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box 
      component="footer" 
      sx={{ 
        backgroundColor: '#1a365d',
        color: '#fff',
        py: 2,
        px: 3,
        mt: 'auto',
      }}
    >
      <Box sx={{ maxWidth: 900, mx: 'auto' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <ApiIcon sx={{ fontSize: 18 }} />
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            API Response Details
          </Typography>
        </Box>
        <Divider sx={{ borderColor: 'rgba(255,255,255,0.2)', mb: 1 }} />
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 2,
          fontSize: '0.75rem',
        }}>
          <Box>
            <Typography variant="caption" sx={{ opacity: 0.7, display: 'block' }}>
              Endpoint
            </Typography>
            <Typography variant="caption" sx={{ fontFamily: 'monospace', wordBreak: 'break-all' }}>
              {metadata.requestUrl}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ opacity: 0.7, display: 'block' }}>
              Response Time
            </Typography>
            <Typography variant="caption">
              {metadata.responseTime}ms
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ opacity: 0.7, display: 'block' }}>
              Status Code
            </Typography>
            <Typography variant="caption" sx={{ 
              color: metadata.statusCode === 200 ? '#4caf50' : '#ff9800',
              fontWeight: 600,
            }}>
              {metadata.statusCode}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ opacity: 0.7, display: 'block' }}>
              Cards Returned
            </Typography>
            <Typography variant="caption">
              {metadata.cardCount ?? 'N/A'}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ opacity: 0.7, display: 'block' }}>
              Patient ID
            </Typography>
            <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
              {metadata.patientId}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ opacity: 0.7, display: 'block' }}>
              Timestamp
            </Typography>
            <Typography variant="caption">
              {new Date(metadata.timestamp).toLocaleString()}
            </Typography>
          </Box>
        </Box>
        <Divider sx={{ borderColor: 'rgba(255,255,255,0.2)', my: 1 }} />
        <Typography variant="caption" sx={{ opacity: 0.5 }}>
          CDS Hooks Sandbox v{appVersion}
        </Typography>
      </Box>
    </Box>
  );
};

ApiFooter.propTypes = {
  metadata: PropTypes.object,
};

/**
 * Top-level component of the EHR Care Gap Dashboard.
 */
export class MainView extends Component {
  render() {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Backdrop
          sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
          open={this.props.isLoadingData}
        >
          <CircularProgress color="inherit" />
        </Backdrop>
        <div className={styles.pin}>
          <Header />
        </div>
        <div className={styles.container}>
          <PatientView />
        </div>
        <ApiFooter metadata={this.props.apiMetadata} />
      </Box>
    );
  }
}

MainView.propTypes = propTypes;

const mapStateToProps = (state) => ({
  isLoadingData: state.uiState.isLoadingData,
  apiMetadata: state.patientState.apiMetadata,
});

export default connect(mapStateToProps)(MainView);
