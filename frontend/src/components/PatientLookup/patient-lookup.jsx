import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import SearchIcon from '@mui/icons-material/Search';
import InputAdornment from '@mui/material/InputAdornment';

import retrievePatient from '../../retrieve-data-helpers/patient-retrieval';

const propTypes = {
  /**
   * The patient ID to seed the input with (the patient currently in context)
   */
  currentPatientId: PropTypes.string,
  /**
   * The URL of the CDS API endpoint
   */
  currentFhirServer: PropTypes.string.isRequired,
  /**
   * Flag to disable the button and show progress while a request is in flight
   */
  isLoadingData: PropTypes.bool.isRequired,
};

/**
 * Patient ID lookup control. The user enters a patient ID and submits to fetch care gap data
 * from the CDS API.
 */
export class PatientLookup extends Component {
  constructor(props) {
    super(props);
    const params = new URLSearchParams(window.location.search);
    this.state = {
      userInput: params.get('patientId') || props.currentPatientId || '',
    };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);
  }

  handleChange(e) {
    this.setState({ userInput: e.target.value });
  }

  handleKeyDown(e) {
    if (e.key === 'Enter') {
      this.handleSubmit();
    }
  }

  handleSubmit() {
    const id = this.state.userInput.trim();
    if (!id) { return; }
    retrievePatient(id).catch(() => {});
  }

  render() {
    return (
      <Paper 
        elevation={0} 
        sx={{ 
          p: 3, 
          backgroundColor: '#fff', 
          borderRadius: 2,
          border: '1px solid #e0e0e0',
        }}
      >
        <Box sx={{
          display: 'flex', gap: 2, alignItems: 'flex-start', flexWrap: 'wrap',
        }}
        >
          <TextField
            label="Patient ID"
            variant="outlined"
            size="medium"
            value={this.state.userInput}
            onChange={this.handleChange}
            onKeyDown={this.handleKeyDown}
            placeholder="Enter patient ID"
            helperText={`CDS API: ${this.props.currentFhirServer}`}
            sx={{ 
              minWidth: 350,
              '& .MuiOutlinedInput-root': {
                backgroundColor: '#fafafa',
              },
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
            }}
          />
          <Button
            variant="contained"
            onClick={this.handleSubmit}
            disabled={this.props.isLoadingData || !this.state.userInput.trim()}
            sx={{ 
              mt: 0.5,
              px: 4,
              py: 1.5,
              backgroundColor: '#1a365d',
              '&:hover': {
                backgroundColor: '#2d4a7c',
              },
            }}
          >
            {this.props.isLoadingData ? 'Searching...' : 'Search Care Gaps'}
          </Button>
        </Box>
      </Paper>
    );
  }
}

PatientLookup.propTypes = propTypes;

const mapStateToProps = (state) => ({
  currentPatientId: state.patientState.currentPatient
    ? state.patientState.currentPatient.id
    : state.patientState.defaultPatientId,
  currentFhirServer: state.fhirServerState.currentFhirServer,
  isLoadingData: state.uiState.isLoadingData,
});

export default connect(mapStateToProps)(PatientLookup);
