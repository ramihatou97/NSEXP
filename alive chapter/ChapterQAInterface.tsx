// frontend/src/components/intelligent/ChapterQAInterface.tsx
/**
 * Chapter Q&A Interface Component
 * Enables intelligent Q&A within chapter context with seamless integration
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box, Paper, TextField, Button, IconButton, Typography,
  List, ListItem, ListItemText, ListItemIcon, Chip,
  Dialog, DialogTitle, DialogContent, DialogActions,
  LinearProgress, Alert, Tooltip, Fade, Popper,
  Avatar, Card, CardContent, Collapse, Divider
} from '@mui/material';
import {
  Send as SendIcon,
  QuestionAnswer as QuestionIcon,
  Psychology as AIIcon,
  Search as SearchIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  AutoAwesome as MagicIcon,
  Source as SourceIcon,
  Close as CloseIcon
} from '@mui/icons-material';

interface ChapterQAInterfaceProps {
  chapterId: string;
  chapterContent: string;
  onContentUpdate: (updatedContent: string) => void;
  currentSection?: string;
  userId?: string;
}

interface QAHistoryItem {
  question: string;
  answer: string;
  timestamp: Date;
  confidence: number;
  sources: Array<{ title: string; credibility: string }>;
  integrated: boolean;
}

interface Source {
  source_id: string;
  source_name: string;
  credibility: string;
  relevance: number;
}

const ChapterQAInterface: React.FC<ChapterQAInterfaceProps> = ({
  chapterId,
  chapterContent,
  onContentUpdate,
  currentSection = '',
  userId = 'default_user'
}) => {
  // State
  const [question, setQuestion] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showInterface, setShowInterface] = useState(false);
  const [qaHistory, setQaHistory] = useState<QAHistoryItem[]>([]);
  const [currentAnswer, setCurrentAnswer] = useState<any>(null);
  const [showIntegration, setShowIntegration] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [expandedHistory, setExpandedHistory] = useState<number[]>([]);

  const inputRef = useRef<HTMLInputElement>(null);
  const popperRef = useRef<HTMLDivElement>(null);

  // Handle text selection for contextual Q&A
  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      if (selection && selection.toString().trim()) {
        setSelectedText(selection.toString());
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        // Create anchor element for popper
        const virtualAnchor = {
          getBoundingClientRect: () => rect,
          clientWidth: 0,
          clientHeight: 0
        } as HTMLElement;

        setAnchorEl(virtualAnchor);
      } else {
        setAnchorEl(null);
        setSelectedText('');
      }
    };

    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('keyup', handleSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('keyup', handleSelection);
    };
  }, []);

  // Submit question
  const handleSubmitQuestion = useCallback(async () => {
    if (!question.trim() || isProcessing) return;

    setIsProcessing(true);

    try {
      const response = await fetch('/api/v1/alive-chapters/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          chapter_id: chapterId,
          chapter_content: chapterContent,
          section_context: currentSection || selectedText || chapterContent.substring(0, 500),
          urgency: 3
        })
      });

      const data = await response.json();

      if (data.status === 'success') {
        const historyItem: QAHistoryItem = {
          question,
          answer: data.answer,
          timestamp: new Date(),
          confidence: data.confidence,
          sources: data.sources?.map((s: Source) => ({
            title: s.source_name,
            credibility: s.credibility
          })) || [],
          integrated: data.auto_integrated
        };

        setQaHistory([historyItem, ...qaHistory]);
        setCurrentAnswer(data);

        // Show integration dialog if auto-integrated
        if (data.auto_integrated && data.integrated_chapter) {
          setShowIntegration(true);
        }

        // Clear question
        setQuestion('');
      }
    } catch (error) {
      console.error('Error processing question:', error);
    } finally {
      setIsProcessing(false);
    }
  }, [question, chapterId, chapterContent, currentSection, selectedText, qaHistory]);

  // Apply integrated content
  const handleApplyIntegration = useCallback(() => {
    if (currentAnswer?.integrated_chapter) {
      onContentUpdate(currentAnswer.integrated_chapter);
      setShowIntegration(false);
      setCurrentAnswer(null);
    }
  }, [currentAnswer, onContentUpdate]);

  // Toggle history item expansion
  const toggleHistoryExpansion = (index: number) => {
    setExpandedHistory(prev =>
      prev.includes(index)
        ? prev.filter(i => i !== index)
        : [...prev, index]
    );
  };

  // Get confidence color
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  // Get credibility icon
  const getCredibilityIcon = (credibility: string) => {
    switch (credibility) {
      case 'gold_standard':
      case 'high':
        return <CheckIcon color="success" fontSize="small" />;
      case 'moderate':
        return <InfoIcon color="info" fontSize="small" />;
      default:
        return <WarningIcon color="warning" fontSize="small" />;
    }
  };

  return (
    <>
      {/* Floating Q&A Button */}
      <Tooltip title="Ask AI Assistant">
        <IconButton
          onClick={() => setShowInterface(!showInterface)}
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            backgroundColor: 'primary.main',
            color: 'white',
            '&:hover': {
              backgroundColor: 'primary.dark',
              transform: 'scale(1.1)'
            },
            zIndex: 1000
          }}
        >
          <QuestionIcon />
        </IconButton>
      </Tooltip>

      {/* Selection Popup */}
      <Popper
        ref={popperRef}
        open={Boolean(anchorEl) && selectedText.length > 0}
        anchorEl={anchorEl}
        placement="top"
        transition
      >
        {({ TransitionProps }) => (
          <Fade {...TransitionProps} timeout={350}>
            <Paper
              elevation={8}
              sx={{
                p: 1,
                display: 'flex',
                gap: 1,
                alignItems: 'center',
                maxWidth: 300
              }}
            >
              <Typography variant="caption" sx={{ flex: 1 }}>
                Ask about: "{selectedText.substring(0, 50)}..."
              </Typography>
              <IconButton
                size="small"
                onClick={() => {
                  setQuestion(`Explain: ${selectedText}`);
                  setShowInterface(true);
                  setAnchorEl(null);
                }}
              >
                <AIIcon />
              </IconButton>
            </Paper>
          </Fade>
        )}
      </Popper>

      {/* Main Q&A Interface */}
      <Collapse in={showInterface}>
        <Paper
          elevation={4}
          sx={{
            position: 'fixed',
            bottom: 80,
            right: 24,
            width: 400,
            maxHeight: 600,
            display: 'flex',
            flexDirection: 'column',
            zIndex: 999
          }}
        >
          {/* Header */}
          <Box
            sx={{
              p: 2,
              backgroundColor: 'primary.main',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AIIcon />
              <Typography variant="h6">AI Chapter Assistant</Typography>
            </Box>
            <IconButton
              size="small"
              onClick={() => setShowInterface(false)}
              sx={{ color: 'white' }}
            >
              <CloseIcon />
            </IconButton>
          </Box>

          {/* Question Input */}
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <TextField
              ref={inputRef}
              fullWidth
              multiline
              maxRows={3}
              placeholder="Ask any question about this chapter..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmitQuestion();
                }
              }}
              disabled={isProcessing}
              InputProps={{
                endAdornment: (
                  <IconButton
                    onClick={handleSubmitQuestion}
                    disabled={!question.trim() || isProcessing}
                    color="primary"
                  >
                    {isProcessing ? <AIIcon /> : <SendIcon />}
                  </IconButton>
                )
              }}
            />

            {isProcessing && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  Searching across multiple sources...
                </Typography>
                <LinearProgress sx={{ mt: 0.5 }} />
              </Box>
            )}
          </Box>

          {/* Current Answer Display */}
          {currentAnswer && !isProcessing && (
            <Alert
              severity="info"
              sx={{ m: 2, mb: 0 }}
              action={
                currentAnswer.auto_integrated && (
                  <Button size="small" onClick={() => setShowIntegration(true)}>
                    View Integration
                  </Button>
                )
              }
            >
              <Typography variant="subtitle2" gutterBottom>
                Latest Answer (Confidence: {(currentAnswer.confidence * 100).toFixed(0)}%)
              </Typography>
              <Typography variant="body2">
                {currentAnswer.answer.substring(0, 150)}...
              </Typography>
            </Alert>
          )}

          {/* Q&A History */}
          <Box sx={{ flex: 1, overflowY: 'auto', p: 2 }}>
            <Typography variant="subtitle2" gutterBottom color="text.secondary">
              Recent Questions
            </Typography>

            <List dense>
              {qaHistory.map((item, index) => (
                <React.Fragment key={index}>
                  <ListItem
                    sx={{
                      flexDirection: 'column',
                      alignItems: 'stretch',
                      backgroundColor: 'background.paper',
                      borderRadius: 1,
                      mb: 1,
                      border: 1,
                      borderColor: 'divider'
                    }}
                  >
                    {/* Question and Metadata */}
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                      <ListItemIcon>
                        <Avatar sx={{ width: 30, height: 30, backgroundColor: 'primary.light' }}>
                          <QuestionIcon fontSize="small" />
                        </Avatar>
                      </ListItemIcon>

                      <ListItemText
                        primary={
                          <Typography variant="body2" fontWeight="medium">
                            {item.question}
                          </Typography>
                        }
                        secondary={
                          <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                            <Chip
                              label={`${(item.confidence * 100).toFixed(0)}%`}
                              size="small"
                              color={getConfidenceColor(item.confidence)}
                            />
                            {item.integrated && (
                              <Chip
                                icon={<CheckIcon />}
                                label="Integrated"
                                size="small"
                                color="success"
                                variant="outlined"
                              />
                            )}
                            <Typography variant="caption" color="text.secondary">
                              {new Date(item.timestamp).toLocaleTimeString()}
                            </Typography>
                          </Box>
                        }
                      />

                      <IconButton
                        size="small"
                        onClick={() => toggleHistoryExpansion(index)}
                      >
                        {expandedHistory.includes(index) ? <CollapseIcon /> : <ExpandIcon />}
                      </IconButton>
                    </Box>

                    {/* Expanded Answer and Sources */}
                    <Collapse in={expandedHistory.includes(index)}>
                      <Box sx={{ pl: 6, pr: 2, pb: 2, pt: 1 }}>
                        <Typography variant="body2" paragraph>
                          {item.answer}
                        </Typography>

                        {item.sources.length > 0 && (
                          <>
                            <Divider sx={{ my: 1 }} />
                            <Typography variant="caption" color="text.secondary" gutterBottom>
                              Sources:
                            </Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                              {item.sources.map((source, idx) => (
                                <Chip
                                  key={idx}
                                  icon={getCredibilityIcon(source.credibility)}
                                  label={source.title}
                                  size="small"
                                  variant="outlined"
                                />
                              ))}
                            </Box>
                          </>
                        )}
                      </Box>
                    </Collapse>
                  </ListItem>
                </React.Fragment>
              ))}
            </List>

            {qaHistory.length === 0 && (
              <Typography variant="body2" color="text.secondary" textAlign="center">
                No questions asked yet. Try asking something!
              </Typography>
            )}
          </Box>
        </Paper>
      </Collapse>

      {/* Integration Dialog */}
      <Dialog
        open={showIntegration}
        onClose={() => setShowIntegration(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <MagicIcon color="primary" />
            <Typography variant="h6">Knowledge Integration</Typography>
          </Box>
        </DialogTitle>

        <DialogContent dividers>
          {currentAnswer && (
            <>
              <Alert severity="success" sx={{ mb: 2 }}>
                The answer has been automatically integrated into your chapter with{' '}
                {(currentAnswer.confidence * 100).toFixed(0)}% confidence.
              </Alert>

              {currentAnswer.integration_analysis && (
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      Integration Analysis
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <Typography variant="body2">
                        <strong>Type:</strong> {currentAnswer.integration_analysis.type}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Clinical Relevance:</strong>{' '}
                        {(currentAnswer.integration_analysis.medical_context?.clinical_relevance * 100).toFixed(0)}%
                      </Typography>
                      <Typography variant="body2">
                        <strong>Concepts Added:</strong>{' '}
                        {currentAnswer.integration_analysis.medical_context?.concepts_added?.join(', ') || 'None'}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={() => setShowIntegration(false)}>
            Review Later
          </Button>
          <Button
            onClick={handleApplyIntegration}
            variant="contained"
            startIcon={<CheckIcon />}
          >
            Apply Integration
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ChapterQAInterface;