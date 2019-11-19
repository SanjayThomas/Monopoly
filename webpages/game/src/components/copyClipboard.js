import React, { useEffect, useCallback, useMemo, useState, useRef } from 'react';
import { faCopy } from '@fortawesome/free-solid-svg-icons/faCopy';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import copy from 'copy-to-clipboard';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Tooltip from 'react-bootstrap/Tooltip';
import PropTypes from 'prop-types';

const COPIED_TEXT = 'Copied!';

export const CopyClipboard = ({ name,content,styles }) => {
  const [text, setText] = useState(content);
  let timerID = useRef(null); 
  
  const textToCopy = useMemo(
    () => `${name}`,
    [name],
  );

  const handleCopy = useCallback(() => {
    copy(textToCopy);
    setText(COPIED_TEXT);
    timerID.current = setTimeout(() => setText(content), 2000);

  }, [textToCopy]);

  useEffect(() => {
    return () => {
      if (timerID.current) clearTimeout(timerID.current);
      timerID.current = null;
    };
  }, []);

  return (
    <OverlayTrigger
      overlay={<Tooltip id={`copy-${name}-tooltip`}>{text}</Tooltip>}
    >
      <a onClick={handleCopy} style={{marginLeft: '4px', marginRight: '4px'}}>
        <FontAwesomeIcon icon={faCopy} />
        <span className="sr-only">{`${name}`}</span>
      </a>
    </OverlayTrigger>
  );
};

CopyClipboard.propTypes = {
  name: PropTypes.string,
  style: PropTypes.string
}

CopyClipboard.defaultProps = {
  name: '', //the value which is copied onto the clipboard
  content: 'Copy game ID',
  style: ''
}