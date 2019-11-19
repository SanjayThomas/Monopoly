import React from 'react';
import { Match } from './match.js';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

/**
 * Returns an array with arrays of the given size.
 *
 * @param myArray {Array} Array to split
 * @param chunkSize {Integer} Size of every group
 */
function chunkArray(myArray, chunk_size){
    var results = [];
    
    while (myArray.length) {
        results.push(myArray.splice(0, chunk_size));
    }
    
    return results;
}

export function BracketGame(props) {
  const chunkSize = 3;

  return (
    <div>
      <h1 style={{ textDecoration: 'underline' }}>Tournament Bracket Game {props.id}</h1>

      {props.bracket.map((round, index) => {

        return (
          <div>
            <h2 style={{ textDecoration: 'underline' }}>Round {index+1}</h2>

            {
              chunkArray(round,chunkSize).map((chunk, index) => {
                return (
                  <Row>
                    {chunk.length > 0 ? <Col><Match id={chunkSize*index+1} totalGames={props.totalGames} results={chunk[0]}/></Col> : ''}
                    {chunk.length > 1 ? <Col><Match id={chunkSize*index+2} totalGames={props.totalGames} results={chunk[1]}/></Col> : ''}
                    {chunk.length > 2 ? <Col><Match id={chunkSize*index+3} totalGames={props.totalGames} results={chunk[2]}/></Col> : ''}
                  </Row>
                );
              })
            }
          </div>
        );
      })}
    </div>
  );
}